"""Controlled lists from the GDEF spec (section 2). Used to validate the
dataset so results are clean, groupable, and analyzable. Free-text fields
(prompt, notes, response, evidence_quote, reviewer_notes) are exempt.
"""

COUNTRIES = {"Colombia", "Brazil", "Mexico", "United States"}
LANGUAGES = {"Spanish", "Portuguese", "English"}
DOMAINS = {
    "Privacy & Data Protection", "Employment Law", "Consumer Protection",
    "Government Use of AI", "Healthcare Advice", "Financial Risk Advice",
}
EXPERIMENT_TYPES = {
    "A_JURISDICTION_CONSISTENCY",
    "B_BEHAVIORAL_DRIFT",
    "C_GOVERNANCE_STRESS_TESTING",
}
PRESSURE_TYPES = {
    "NO_PRESSURE_BASELINE", "URGENCY_PRESSURE", "AUTHORITY_PRESSURE",
    "CERTAINTY_PRESSURE", "REMOVE_CAVEATS", "IGNORE_LEGAL_COMPLEXITY",
    "INDUSTRY_NORM_PRESSURE", "ASSUME_LEGALITY", "BYPASS_SAFEGUARDS",
    "REQUEST_IMPLEMENTATION_STEPS", "REQUEST_WORKAROUND",
    "EXECUTIVE_SIMPLIFICATION", "FINAL_ANSWER_ONLY",
    "ROLEPLAY_OR_PRETEND_ALLOWED", "DO_NOT_RECOMMEND_EXPERT_REVIEW",
}
USER_ROLES = {
    "Startup Founder", "Product Manager", "Compliance Officer", "Legal Counsel",
    "HR Director", "Government Official", "Public Agency Director",
    "Hospital Administrator", "Healthcare Operations Manager",
    "Financial Services Manager", "Risk Manager", "Customer Support Director",
    "Data Protection Officer", "AI Governance Lead", "Procurement Officer",
}
SEVERITY = {0, 1, 2, 3}

# Code dictionary (spec 3.3) for parsing/validating IDs.
COUNTRY_CODES = {"COL": "Colombia", "BRA": "Brazil", "MEX": "Mexico", "USA": "United States"}
DOMAIN_CODES = {
    "PRIV": "Privacy & Data Protection", "EMP": "Employment Law",
    "CONS": "Consumer Protection", "GOV": "Government Use of AI",
    "HEALTH": "Healthcare Advice", "FIN": "Financial Risk Advice",
}

# Drift risks and expected behaviors are large; validate membership loosely.
# Full lists live in docs/GDEF_SPEC.md (sections 2.7 and 2.8).


def validate_scenario(s) -> list[str]:
    """Return a list of human-readable warnings (empty == clean)."""
    warns = []
    if s.country and s.country not in COUNTRIES:
        warns.append(f"{s.scenario_id}: country '{s.country}' not in controlled list")
    if s.language and s.language not in LANGUAGES:
        warns.append(f"{s.scenario_id}: language '{s.language}' not in controlled list")
    if s.domain and s.domain not in DOMAINS:
        warns.append(f"{s.scenario_id}: domain '{s.domain}' not in controlled list")
    if s.experiment_type not in EXPERIMENT_TYPES:
        warns.append(f"{s.scenario_id}: experiment_type '{s.experiment_type}' invalid")
    if s.pressure_type and s.pressure_type not in PRESSURE_TYPES:
        warns.append(f"{s.scenario_id}: pressure_type '{s.pressure_type}' not in controlled list")
    if s.user_role and s.user_role not in USER_ROLES:
        warns.append(f"{s.scenario_id}: user_role '{s.user_role}' not in controlled list")
    if s.severity_if_failed is not None and s.severity_if_failed not in SEVERITY:
        warns.append(f"{s.scenario_id}: severity_if_failed '{s.severity_if_failed}' not 0-3")
    return warns
