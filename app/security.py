import os, secrets
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
SESSION_SECRET = os.getenv("CYBERSENTINEL_SESSION_SECRET", "dev-only-change-me")
COOKIE_SECURE = os.getenv("CYBERSENTINEL_COOKIE_SECURE", "0") == "1"

def hash_password(password: str) -> str:
    return pwd.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd.verify(password, password_hash)

def login_session(request, user):
    request.session.clear()
    request.session["user_id"] = user.id
    request.session["username"] = user.username
    request.session["role"] = user.role
    request.session["csrf"] = secrets.token_urlsafe(32)

def csrf_ok(request, token: str) -> bool:
    expected = request.session.get("csrf", "")
    return bool(expected and token and secrets.compare_digest(expected, token))

def allowed(request, roles):
    return request.session.get("role") in roles
