from types import SimpleNamespace
from app.applicability import screen

def test_finance_personal_data_screen():
    org=SimpleNamespace(processes_personal_data=True,financial_entity=True,product_manufacturer=False,sector="Banking",employee_band="250+",essential_service=True,digital_provider_category="")
    result={x[0]:x[1] for x in screen(org)}
    assert result["GDPR"]=="LIKELY_APPLICABLE"
    assert result["DORA"]=="LIKELY_APPLICABLE"
    assert result["NIS2"]=="LIKELY_APPLICABLE"
