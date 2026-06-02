

import re
from typing import Any

ROUTE_FAST_TRACK = "Fast-track"
ROUTE_MANUAL_REVIEW = "Manual Review"
ROUTE_INVESTIGATION = "Investigation Flag"
ROUTE_SPECIALIST = "Specialist Queue"

FRAUD_KEYWORDS: list[str] = [
    "fraud",
    "fraudulent",
    "inconsistent",
    "inconsistency",
    "staged",
    "fabricated",
    "false claim",
    "fake",
    "suspicious",
]

FAST_TRACK_THRESHOLD = 25_000.0  # USD



def _contains_fraud_keywords(text: str) -> list[str]:
    """Return list of fraud keywords found in text."""
    text_lower = text.lower()
    return [kw for kw in FRAUD_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", text_lower)]


def _is_injury_claim(claim_type: str) -> bool:
    ct = (claim_type or "").lower()
    return any(w in ct for w in ("injur", "bodily", "medical", "liability"))


def _get_amount(value: Any) -> float | None:
    """Safely convert to float."""
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return None


# ── Main router ──────────────────────────────────────────────────────────────

def route_claim(extracted: dict, validation: dict) -> dict:
    """
    Determine the recommended routing queue and produce a reasoning string.

    Args:
        extracted   : dict from field_extractor.extract_fields()
        validation  : dict from validator.validate()

    Returns:
        {
            "recommended_route" : str,
            "reasoning"         : str,
            "flags"             : list[str],   # any additional flags
        }
    """
    flags: list[str] = []
    reasoning_parts: list[str] = []

    # ── Gather inputs ────────────────────────────────────────────────────────
    description = (extracted.get("incident_description") or "").strip()
    description += " " + (extracted.get("damage_description") or "")

    claim_type = (extracted.get("claim_type") or "").strip()
    missing_fields = validation.get("missing_fields", [])
    inconsistencies = validation.get("inconsistencies", [])

    damage_amount = _get_amount(extracted.get("estimated_damage_amount"))
    initial_estimate = _get_amount(extracted.get("initial_estimate"))
    # Use whichever is available; prefer damage_amount
    amount = damage_amount if damage_amount is not None else initial_estimate

    is_injury = _is_injury_claim(claim_type)

    fraud_hits = _contains_fraud_keywords(description)
    has_fraud_flag = len(fraud_hits) > 0

    # ── Determine primary route (priority order) ─────────────────────────────
    route = ROUTE_FAST_TRACK  # default optimistic route

    # Priority 1: Manual Review if mandatory fields are missing
    if missing_fields:
        route = ROUTE_MANUAL_REVIEW
        reasoning_parts.append(
            f"Mandatory fields are missing ({', '.join(missing_fields)}), "
            "preventing automated processing."
        )

    # Priority 2: Investigation Flag if fraud keywords detected
    if has_fraud_flag:
        route = ROUTE_INVESTIGATION
        flags.append(ROUTE_INVESTIGATION)
        reasoning_parts.append(
            f"Fraud-related keyword(s) detected in the incident description "
            f"({', '.join(fraud_hits)}). Claim requires SIU investigation."
        )

    # Priority 3: Specialist Queue for injury claims
    if is_injury:
        route = ROUTE_SPECIALIST
        reasoning_parts.append(
            f"Claim type is '{claim_type}', which involves bodily injury. "
            "Routing to Specialist Queue for medical review and liability assessment."
        )

    # Priority 4: Fast-track if damage is below threshold (and no higher priority triggered)
    if route == ROUTE_FAST_TRACK:
        if amount is not None and amount < FAST_TRACK_THRESHOLD:
            reasoning_parts.append(
                f"Estimated damage (${amount:,.0f}) is below the $25,000 fast-track threshold "
                "and all mandatory fields are present with no fraud indicators. "
                "Eligible for automated fast-track settlement."
            )
        elif amount is not None and amount >= FAST_TRACK_THRESHOLD:
            route = ROUTE_MANUAL_REVIEW
            reasoning_parts.append(
                f"Estimated damage (${amount:,.0f}) meets or exceeds $25,000. "
                "Routed to Manual Review for adjuster oversight."
            )
        else:
            route = ROUTE_MANUAL_REVIEW
            reasoning_parts.append(
                "Estimated damage amount could not be determined. "
                "Routing to Manual Review as a precaution."
            )

    if inconsistencies:
        flags.extend([f"Inconsistency: {i}" for i in inconsistencies])
        reasoning_parts.append(
            f"Data inconsistencies detected: {'; '.join(inconsistencies)}"
        )

    reasoning = " | ".join(reasoning_parts) if reasoning_parts else "No special conditions detected."

    return {
        "recommended_route": route,
        "reasoning": reasoning,
        "flags": flags,
    }


# ── Blank-form short-circuit ──────────────────────────────────────────────────

def route_blank_form(file_name: str) -> dict:
    """Return a standard Manual Review result for blank / template PDFs."""
    return {
        "recommended_route": ROUTE_MANUAL_REVIEW,
        "reasoning": (
            f"Document '{file_name}' appears to be a blank or template form with no claimant data. "
            "Manual review required to obtain a completed FNOL submission."
        ),
        "flags": ["Blank/Template Form — No Claimant Data"],
    }
