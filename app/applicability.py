NIS2_SECTORS = {
    "Energy", "Transport", "Banking", "Financial market infrastructures", "Health",
    "Drinking water", "Waste water", "Digital infrastructure", "ICT service management",
    "Public administration", "Space", "Postal and courier services", "Waste management",
    "Chemicals", "Food", "Manufacturing", "Digital providers", "Research"
}

IR_2690_CATEGORIES = {
    "DNS service provider", "TLD name registry", "Cloud computing service provider",
    "Data centre service provider", "Content delivery network provider", "Managed service provider",
    "Managed security service provider", "Online marketplace", "Online search engine",
    "Social networking services platform", "Trust service provider"
}

def screen(org):
    results = []

    if org.processes_personal_data:
        results.append(("GDPR", "LIKELY_APPLICABLE", "High", "Organisation indicates processing of personal data. Exact territorial/material scope still requires verification."))
    else:
        results.append(("GDPR", "REVIEW", "Screening", "No personal-data processing was indicated; verify whether any personal data is processed in practice."))

    if org.financial_entity:
        results.append(("DORA", "LIKELY_APPLICABLE", "Medium", "Organisation self-identifies as a financial entity. DORA entity-category scope must still be verified."))
    else:
        results.append(("DORA", "REVIEW", "Screening", "Financial-entity status not indicated. Verify whether the organisation falls within a DORA entity category."))

    if org.product_manufacturer:
        results.append(("CRA", "LIKELY_APPLICABLE", "Medium", "Organisation indicates it manufactures or places products with digital elements on the market. Role/product exclusions and transition dates require verification."))
    else:
        results.append(("CRA", "REVIEW", "Screening", "Manufacturer status not indicated. CRA may still be relevant depending on economic-operator role and products."))

    medium_or_larger = org.employee_band in {"50-249", "250+"}
    if org.sector in NIS2_SECTORS and (medium_or_larger or org.essential_service):
        results.append(("NIS2", "LIKELY_APPLICABLE", "Medium", "Sector and size/essential-service answers indicate potential NIS2 scope. Member-State transposition and entity classification must be verified."))
    elif org.sector in NIS2_SECTORS:
        results.append(("NIS2", "REVIEW", "Screening", "Sector is within a NIS2-related category, but size and special-scope rules require legal verification."))
    else:
        results.append(("NIS2", "REVIEW", "Screening", "Selected sector did not trigger this screening rule; special entities and national transposition may still create scope."))

    if org.digital_provider_category in IR_2690_CATEGORIES:
        results.append(("NIS2-IR-2024-2690", "LIKELY_APPLICABLE", "Medium", "Selected digital-provider category is among categories named by Commission Implementing Regulation (EU) 2024/2690; exact scope must be verified."))
    else:
        results.append(("NIS2-IR-2024-2690", "REVIEW", "Screening", "No matching provider category selected; verify exact entity category before excluding the implementing regulation."))

    results.append(("CSA", "REFERENCE", "Screening", "EU Cybersecurity Act certification framework is tracked as a reference layer; scheme applicability depends on products/services and relevant certification schemes."))
    return results
