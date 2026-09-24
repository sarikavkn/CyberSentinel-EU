import csv, hashlib, io, json, os, secrets
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from .db import Base, engine, SessionLocal, get_db
from .models import User, Organization, ApplicabilityResult, Assessment, Evidence, Finding, Risk, Asset, AuditLog
from .security import hash_password, verify_password, login_session, csrf_ok, allowed, SESSION_SECRET, COOKIE_SECURE
from .applicability import screen, NIS2_SECTORS, IR_2690_CATEGORIES

BASE = Path(__file__).resolve().parent.parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
REG = json.loads((BASE / "regulatory/frameworks_and_requirements.json").read_text(encoding="utf-8"))
CONTROLS = json.loads((BASE / "regulatory/controls.json").read_text(encoding="utf-8"))
REQ_BY_CODE = {r["code"]: r for r in REG["requirements"]}
ALLOWED_EXT = {".pdf", ".txt", ".csv", ".json", ".png", ".jpg", ".jpeg", ".log"}
MAX_UPLOAD = 10 * 1024 * 1024

Base.metadata.create_all(bind=engine)
app = FastAPI(title="CyberSentinel EU", version="1.5.0")
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax", max_age=3600, https_only=COOKIE_SECURE)
templates = Jinja2Templates(directory=str(BASE / "app/templates"))
app.mount("/static", StaticFiles(directory=str(BASE / "app/static")), name="static")

def add_audit(db, actor, action, target="", details=""):
    db.add(AuditLog(actor=actor, action=action, target=target, details=details))
    db.commit()

def seed():
    db = SessionLocal()
    try:
        if not db.scalar(select(User).where(User.username == "admin")):
            db.add(User(username=os.getenv("CYBERSENTINEL_ADMIN_USER", "admin"), password_hash=hash_password(os.getenv("CYBERSENTINEL_ADMIN_PASSWORD", "ChangeMe!2026")), role="Admin"))
        if not db.scalar(select(Organization).limit(1)):
            db.add(Organization(name="Demo EU Organisation", country="EU", sector="General", employee_band="Unknown"))
        db.commit()
    finally:
        db.close()
seed()

def require_login(request):
    if not request.session.get("user_id"):
        raise HTTPException(401, "Authentication required")

def html_auth(request):
    return bool(request.session.get("user_id"))

def template_ctx(request, **kwargs):
    return {"request": request, "csrf": request.session.get("csrf", ""), "role": request.session.get("role", ""), **kwargs}

@app.get("/health")
def health():
    return {"status":"ok","version":"1.5.0","time":datetime.now(timezone.utc).isoformat()}

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login_post(request: Request, username: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    user = db.scalar(select(User).where(User.username == username, User.active == True))
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request":request,"error":"Invalid username or password."}, status_code=401)
    login_session(request, user)
    add_audit(db, user.username, "LOGIN")
    return RedirectResponse("/", 303)

@app.post("/logout")
def logout(request: Request, csrf: str=Form(...), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403, "CSRF validation failed")
    add_audit(db, request.session.get("username","unknown"), "LOGOUT")
    request.session.clear()
    return RedirectResponse("/login", 303)

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login", 303)
    assessments = db.scalars(select(Assessment)).all()
    scored = [a for a in assessments if a.applicability != "NOT_APPLICABLE"]
    avg = round(sum(a.score for a in scored) / len(scored), 1) if scored else 0
    ctx = template_ctx(request,
        frameworks=REG["frameworks"], total=len(REG["requirements"]), assessed=len(assessments),
        open_findings=db.scalar(select(func.count(Finding.id)).where(Finding.status != "CLOSED")) or 0,
        evidence=db.scalar(select(func.count(Evidence.id))) or 0,
        risks=db.scalar(select(func.count(Risk.id)).where(Risk.status == "OPEN")) or 0,
        assets=db.scalar(select(func.count(Asset.id))) or 0, score=avg)
    return templates.TemplateResponse("dashboard.html", ctx)

@app.get("/organization", response_class=HTMLResponse)
def organization_page(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login", 303)
    org=db.scalar(select(Organization).limit(1))
    apps=db.scalars(select(ApplicabilityResult).order_by(ApplicabilityResult.framework)).all()
    return templates.TemplateResponse("organization.html", template_ctx(request, org=org, apps=apps, sectors=sorted(NIS2_SECTORS), provider_categories=sorted(IR_2690_CATEGORIES)))

@app.post("/organization")
def organization_save(request: Request, csrf: str=Form(...), name: str=Form(...), country: str=Form("EU"), sector: str=Form("General"), employee_band: str=Form("Unknown"), financial_entity: str|None=Form(None), product_manufacturer: str|None=Form(None), processes_personal_data: str|None=Form(None), essential_service: str|None=Form(None), digital_provider_category: str=Form(""), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403,"CSRF validation failed")
    org=db.scalar(select(Organization).limit(1))
    if not org:
        org=Organization(name=name); db.add(org)
    org.name=name.strip()[:200]; org.country=country.upper()[:2]; org.sector=sector[:160]; org.employee_band=employee_band[:80]
    org.financial_entity=financial_entity=="on"; org.product_manufacturer=product_manufacturer=="on"; org.processes_personal_data=processes_personal_data=="on"; org.essential_service=essential_service=="on"; org.digital_provider_category=digital_provider_category[:160]
    db.commit()
    for fw,result,confidence,reason in screen(org):
        row=db.scalar(select(ApplicabilityResult).where(ApplicabilityResult.framework==fw))
        if not row: row=ApplicabilityResult(framework=fw); db.add(row)
        row.result=result; row.confidence=confidence; row.reason=reason; row.updated_at=datetime.now(timezone.utc)
    db.commit(); add_audit(db,request.session.get("username","unknown"),"UPDATE_ORGANIZATION",org.name,"Applicability screening refreshed")
    return RedirectResponse("/organization",303)

@app.get("/requirements", response_class=HTMLResponse)
def requirements_page(request: Request, framework: str="", db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login", 303)
    reqs=[r for r in REG["requirements"] if not framework or r["framework"]==framework]
    assessed={a.requirement_code:a for a in db.scalars(select(Assessment)).all()}
    return templates.TemplateResponse("requirements.html", template_ctx(request, requirements=reqs, frameworks=REG["frameworks"], assessed=assessed, selected_framework=framework))

@app.post("/assessments/{code}")
def save_assessment(code: str, request: Request, csrf: str=Form(...), status: str=Form("PARTIAL"), applicability: str=Form("APPLICABLE"), score: float=Form(0), maturity: int=Form(0), owner: str=Form(""), notes: str=Form(""), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403,"CSRF validation failed")
    if code not in REQ_BY_CODE: raise HTTPException(404,"Unknown requirement")
    r=REQ_BY_CODE[code]
    a=db.scalar(select(Assessment).where(Assessment.requirement_code==code))
    if not a: a=Assessment(framework=r["framework"],requirement_code=code); db.add(a)
    a.status=status; a.applicability=applicability; a.score=max(0,min(100,score)); a.maturity=max(0,min(5,maturity)); a.owner=owner[:120]; a.notes=notes[:5000]; a.updated_at=datetime.now(timezone.utc)
    db.commit(); add_audit(db,request.session.get("username","unknown"),"UPDATE_ASSESSMENT",code,f"{status}/{a.score}")
    return RedirectResponse(f"/requirements?framework={r['framework']}",303)

@app.get("/controls", response_class=HTMLResponse)
def controls_page(request: Request):
    if not html_auth(request): return RedirectResponse("/login", 303)
    return templates.TemplateResponse("controls.html", template_ctx(request, controls=CONTROLS))

@app.get("/evidence", response_class=HTMLResponse)
def evidence_page(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login", 303)
    rows=db.scalars(select(Evidence).order_by(Evidence.collected_at.desc())).all()
    return templates.TemplateResponse("evidence.html", template_ctx(request, rows=rows, requirements=REG["requirements"], controls=CONTROLS))

@app.post("/evidence")
async def evidence_upload(request: Request, csrf: str=Form(...), requirement_code: str=Form(...), control_id: str=Form(...), title: str=Form(...), notes: str=Form(""), file: UploadFile=File(...), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403,"CSRF validation failed")
    ext=Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXT: raise HTTPException(400,"File type not allowed")
    data=await file.read(MAX_UPLOAD+1)
    if len(data)>MAX_UPLOAD: raise HTTPException(413,"Evidence file exceeds 10 MB development limit")
    digest=hashlib.sha256(data).hexdigest()
    stored=f"{secrets.token_hex(16)}{ext}"
    (UPLOADS/stored).write_bytes(data)
    e=Evidence(requirement_code=requirement_code,control_id=control_id,title=title[:250],source="upload",evidence_type=ext.lstrip("."),original_filename=(file.filename or "")[:255],stored_filename=stored,size_bytes=len(data),hash_sha256=digest,notes=notes[:5000])
    db.add(e); db.commit(); db.refresh(e); add_audit(db,request.session.get("username","unknown"),"UPLOAD_EVIDENCE",str(e.id),f"sha256={digest}")
    return RedirectResponse("/evidence",303)

@app.get("/evidence/{evidence_id}/download")
def evidence_download(evidence_id: int, request: Request, db: Session=Depends(get_db)):
    require_login(request)
    e=db.get(Evidence,evidence_id)
    if not e or not e.stored_filename: raise HTTPException(404)
    p=UPLOADS/e.stored_filename
    if not p.exists(): raise HTTPException(404)
    add_audit(db,request.session.get("username","unknown"),"DOWNLOAD_EVIDENCE",str(e.id))
    return FileResponse(p, filename=e.original_filename or p.name)

@app.get("/findings", response_class=HTMLResponse)
def findings_page(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login",303)
    rows=db.scalars(select(Finding).order_by(Finding.created_at.desc())).all()
    return templates.TemplateResponse("findings.html", template_ctx(request, rows=rows, requirements=REG["requirements"], controls=CONTROLS))

@app.post("/findings")
def create_finding(request: Request, csrf: str=Form(...), requirement_code: str=Form(...), control_id: str=Form(...), title: str=Form(...), severity: str=Form("Medium"), owner: str=Form(""), due_date: str=Form(""), remediation: str=Form(""), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403)
    f=Finding(requirement_code=requirement_code,control_id=control_id,title=title[:250],severity=severity,owner=owner[:120],due_date=due_date[:30],remediation=remediation[:5000])
    db.add(f); db.commit(); db.refresh(f); add_audit(db,request.session.get("username","unknown"),"CREATE_FINDING",str(f.id),title)
    return RedirectResponse("/findings",303)

@app.get("/risks", response_class=HTMLResponse)
def risks_page(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login",303)
    rows=db.scalars(select(Risk).order_by(Risk.residual_score.desc())).all()
    return templates.TemplateResponse("risks.html", template_ctx(request, rows=rows))

@app.post("/risks")
def create_risk(request: Request, csrf: str=Form(...), title: str=Form(...), category: str=Form("Cyber"), likelihood: int=Form(3), impact: int=Form(3), residual_score: int=Form(9), treatment: str=Form(""), owner: str=Form(""), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403)
    likelihood=max(1,min(5,likelihood)); impact=max(1,min(5,impact)); residual_score=max(1,min(25,residual_score))
    r=Risk(title=title[:250],category=category[:120],likelihood=likelihood,impact=impact,inherent_score=likelihood*impact,residual_score=residual_score,treatment=treatment[:5000],owner=owner[:120])
    db.add(r); db.commit(); db.refresh(r); add_audit(db,request.session.get("username","unknown"),"CREATE_RISK",str(r.id),title)
    return RedirectResponse("/risks",303)

@app.get("/assets", response_class=HTMLResponse)
def assets_page(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login",303)
    rows=db.scalars(select(Asset).order_by(Asset.criticality.desc(),Asset.name)).all()
    return templates.TemplateResponse("assets.html", template_ctx(request, rows=rows))

@app.post("/assets")
def create_asset(request: Request, csrf: str=Form(...), name: str=Form(...), asset_type: str=Form("System"), owner: str=Form(""), criticality: str=Form("Medium"), internet_exposed: str|None=Form(None), contains_personal_data: str|None=Form(None), db: Session=Depends(get_db)):
    require_login(request)
    if not csrf_ok(request, csrf): raise HTTPException(403)
    if db.scalar(select(Asset).where(Asset.name==name.strip())): raise HTTPException(409,"Asset name already exists")
    a=Asset(name=name.strip()[:180],asset_type=asset_type[:80],owner=owner[:120],criticality=criticality,internet_exposed=internet_exposed=="on",contains_personal_data=contains_personal_data=="on")
    db.add(a); db.commit(); db.refresh(a); add_audit(db,request.session.get("username","unknown"),"CREATE_ASSET",str(a.id),a.name)
    return RedirectResponse("/assets",303)

@app.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, db: Session=Depends(get_db)):
    if not html_auth(request): return RedirectResponse("/login",303)
    if not allowed(request,{"Admin","Auditor"}): raise HTTPException(403)
    rows=db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1000)).all()
    return templates.TemplateResponse("audit.html", template_ctx(request, rows=rows))

@app.get("/reports/assessment.csv")
def assessment_csv(request: Request, db: Session=Depends(get_db)):
    require_login(request)
    output=io.StringIO(); w=csv.writer(output)
    w.writerow(["Framework","Requirement Code","Article","Requirement","Applicability","Status","Maturity","Score","Owner","Notes"])
    assessed={a.requirement_code:a for a in db.scalars(select(Assessment)).all()}
    for r in REG["requirements"]:
        a=assessed.get(r["code"])
        w.writerow([r["framework"],r["code"],r["article"],r["title"],a.applicability if a else "REVIEW",a.status if a else "NOT_ASSESSED",a.maturity if a else 0,a.score if a else 0,a.owner if a else "",a.notes if a else ""])
    add_audit(db,request.session.get("username","unknown"),"EXPORT_ASSESSMENT_CSV")
    return StreamingResponse(iter([output.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=cybersentinel_assessment.csv"})

@app.get("/api/regulatory/catalog")
def regulatory_catalog(): return REG

@app.get("/api/controls")
def controls_api(): return CONTROLS

@app.get("/api/audit")
def audit_api(request: Request, db: Session=Depends(get_db)):
    require_login(request)
    if not allowed(request,{"Admin","Auditor"}): raise HTTPException(403)
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1000)).all()
