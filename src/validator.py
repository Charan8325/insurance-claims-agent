"""
validator.py
------------
Identifies missing mandatory fields and inconsistencies in extracted FNOL data.
"""

import re
from typing import Any

# All fields that MUST be present for a complete FNOL submission
MANDATORY_FIELDS: list[str] = [
    "policy_number",
    "policyholder_name",
    "effective_date",
    "expiry_date",
    "date_of_loss",
    "location_of_loss",
    "incident_description",
    "claimant_name",
    "claimant_contact",
    "asset_type",
    "damage_description",
    "estimated_damage_amount",
    "claim_type",
    "initial_estimate",
]

# Fields that are strongly recommended but not strictly mandatory
RECOMMENDED_FIELDS: list[str] = [
    "carrier",
    "time_of_loss",
    "asset_id",
    "attachments",
    "police_report_number",
]

# Minimum number of meaningful field values required before we consider a
# document "real" data (vs a blank template whose labels got extracted).
_BLANK_FORM_THRESHOLD = 4

# Known form-label fragments that should never appear as field values
_LABEL_PATTERNS = [
    r"^\(A/C",           # "(A/C, No, Ext):" etc.
    r"^CONTACT$",
    r"^\(First,\s*Middle",
    r"^NAIC CODE",
    r"^AND TIME AM",
    r"^POLICY OR FIRE",
    r"^POLICE OR FIRE",
    r"^Additional Remarks",
    r"^ACORD\s*\d",
    r"^Y\s*/\s*N",
    r"^HOME\s+BUS",
]


def _is_empty(value: Any) -> bool:
    """Return True when a value is considered absent/empty."""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() in ("", "N/A", "n/a", "None", "null"):
        return True
    return False


def _looks_like_label(value: str) -> bool:
    """Return True if a string looks like an extracted form label rather than real data."""
    for pat in _LABEL_PATTERNS:
        if re.search(pat, value, re.IGNORECASE):
            return True
    return False


def is_blank_form(extracted: dict) -> bool:
    """
    Detect whether the extracted data came from a blank/template PDF
    (i.e. almost no real values were found, or values are clearly form labels).
    Returns True if the document should be flagged as a blank template.
    """
    real_values = 0
    label_hits = 0

    for key, val in extracted.items():
        if isinstance(val, list):
            continue  # lists being empty is fine
        if _is_empty(val):
            continue
        if isinstance(val, (int, float)):
            real_values += 1
            continue
        if isinstance(val, str):
            if _looks_like_label(val):
                label_hits += 1
            else:
                real_values += 1

    # Blank if: more label-hits than real values, OR fewer than threshold real values
    return label_hits > real_values or real_values < _BLANK_FORM_THRESHOLD


def find_missing_fields(extracted: dict) -> list[str]:
    """Return list of mandatory field names that are empty / null."""
    return [f for f in MANDATORY_FIELDS if _is_empty(extracted.get(f))]


def find_recommended_missing(extracted: dict) -> list[str]:
    """Return list of recommended (non-mandatory) fields that are absent."""
    return [f for f in RECOMMENDED_FIELDS if _is_empty(extracted.get(f))]


def _negated_injury(desc: str) -> bool:
    """Return True if the injury mention in desc is negated ('no injuries', etc.)."""
    return bool(re.search(
        r"no injur|injur\w*\s+(were|was)\s+(not|none)|without injur|injuries? (not |were not )?reported",
        desc, re.IGNORECASE
    ))


def find_inconsistencies(extracted: dict) -> list[str]:
    """
    Detect logical inconsistencies in the extracted data.
    Returns a list of human-readable inconsistency descriptions.
    """
    issues = []

    # Damage vs initial estimate mismatch (>20% deviation)
    damage = extracted.get("estimated_damage_amount")
    estimate = extracted.get("initial_estimate")
    if damage and estimate:
        try:
            d, e = float(damage), float(estimate)
            if d > 0 and abs(d - e) / d > 0.20:
                issues.append(
                    f"Estimated damage (${d:,.0f}) and initial estimate (${e:,.0f}) differ by "
                    f"more than 20% — possible data entry error."
                )
        except (TypeError, ValueError):
            pass

    # Claim type mismatch — with negation awareness
    desc = (extracted.get("incident_description") or "").lower()
    claim_type = (extracted.get("claim_type") or "").lower()

    # Injury: only flag when mention is NOT negated ("no injuries", "injuries were not reported")
    if "injur" in desc and not _negated_injury(desc) and claim_type not in ("injury", "bodily injury"):
        issues.append(
            "Incident description mentions injury but claim_type is not 'Injury'."
        )

    # Fire
    if ("fire" in desc or "burn" in desc) and claim_type not in ("fire", "property damage"):
        issues.append(
            "Incident description mentions fire but claim_type may not reflect this."
        )

    # Theft
    if ("theft" in desc or "stolen" in desc) and "theft" not in claim_type:
        issues.append(
            "Incident description mentions theft but claim_type is not 'Theft'."
        )

    return issues


def validate(extracted: dict) -> dict:
    """
    Full validation pass.
    Returns:
        {
            "missing_fields"        : [...],
            "recommended_missing"   : [...],
            "inconsistencies"       : [...],
            "is_complete"           : bool,
            "is_blank_form"         : bool,
        }
    """
    blank = is_blank_form(extracted)
    missing = find_missing_fields(extracted)
    recommended_missing = find_recommended_missing(extracted)
    inconsistencies = [] if blank else find_inconsistencies(extracted)

    return {
        "missing_fields": missing,
        "recommended_missing": recommended_missing,
        "inconsistencies": inconsistencies,
        "is_complete": len(missing) == 0 and not blank,
        "is_blank_form": blank,
    }
