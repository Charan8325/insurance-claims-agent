

import json
import re
import os
from typing import Optional

# ── Try to import the Anthropic SDK ─────────────────────────────────────────
try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


EXTRACTION_PROMPT = """You are an expert insurance claims processor. Given the raw text extracted
from a First Notice of Loss (FNOL) document, extract the following fields and return ONLY valid JSON.

FIELDS TO EXTRACT:
Policy Information:
  - policy_number
  - policyholder_name
  - effective_date
  - expiry_date
  - carrier

Incident Information:
  - date_of_loss
  - time_of_loss
  - location_of_loss
  - incident_description
  - police_report_number

Involved Parties:
  - claimant_name
  - claimant_contact
  - third_parties (list)
  - witnesses (list)

Asset Details:
  - asset_type
  - asset_id  (VIN / property address / other identifier)
  - asset_description
  - damage_description
  - estimated_damage_amount  (numeric value only, in USD, e.g. 8500)

Other Mandatory Fields:
  - claim_type  (one of: "Property Damage", "Injury", "Theft", "Fire", "Other")
  - attachments (list of described attachments)
  - initial_estimate (numeric value only, in USD)

RULES:
- If a field cannot be found in the text, set its value to null.
- For numeric fields (estimated_damage_amount, initial_estimate), extract only the numeric value.
  E.g. "$8,500" → 8500. If not found, use null.
- For list fields (third_parties, witnesses, attachments), return an empty list [] if none found.
- Return ONLY the JSON object, no markdown fences, no explanation.

FNOL DOCUMENT TEXT:
{fnol_text}
"""



def extract_with_claude(fnol_text: str, api_key: Optional[str] = None) -> dict:

    if not _ANTHROPIC_AVAILABLE:
        raise ImportError("The 'anthropic' package is not installed. Run: pip install anthropic")

    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError("ANTHROPIC_API_KEY not set and no api_key provided.")

    client = anthropic.Anthropic(api_key=key)

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT.format(fnol_text=fnol_text[:12000]),  # token guard
            }
        ],
    )

    raw = message.content[0].text.strip()
  
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)



def _find(pattern: str, text: str, flags=re.IGNORECASE) -> Optional[str]:
    """Return the first captured group or None."""
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else None


def _parse_amount(raw: Optional[str]) -> Optional[float]:
    """Convert '$8,500' → 8500.0, handling None gracefully."""
    if not raw:
        return None
    digits = re.sub(r"[^\d.]", "", raw)
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def extract_with_regex(fnol_text: str) -> dict:
    """
    Heuristic regex-based field extraction from FNOL text.
    Less accurate than Claude but works without an API key.
    """
    t = fnol_text  # shorthand

   
    def lv(labels: list[str]) -> Optional[str]:
        for label in labels:
            pat = rf"(?:{re.escape(label)})[:\s]+([^\n]+)"
            val = _find(pat, t)
            if val:
                return val.strip()
        return None

    # Policy
    policy_number = lv(["Policy Number", "POLICY NUMBER", "Policy #"])
    policyholder_name = lv(["Policyholder Name", "NAME OF INSURED", "Insured Name"])
    effective_date = lv(["Policy Effective Date", "Effective Date", "EFFECTIVE DATE"])
    expiry_date = lv(["Policy Expiry Date", "Expiry Date", "Expiration Date"])
    carrier = lv(["Carrier", "CARRIER", "Insurance Company"])

    # Incident
    date_of_loss = lv(["Date of Loss", "DATE OF LOSS", "Loss Date"])
    time_of_loss = lv(["Time of Loss", "TIME OF LOSS", "Loss Time"])
    location_of_loss = lv(["Location of Loss", "LOCATION OF LOSS"])
    police_report = lv(["Police.*Report", "Report #", "Report Number", "REPORT NUMBER"])

    desc_match = re.search(
        r"(?:Description of Accident|DESCRIPTION OF ACCIDENT)[:\s]+(.+?)(?:\n(?:INVOLVED|INSURED|ASSET|OTHER|CLAIMANT|THIRD|WITNESS|POLICY|INCIDENT)[A-Z \t]+\n|\Z)",
        t, re.IGNORECASE | re.DOTALL
    )
    incident_description = desc_match.group(1).strip()[:800] if desc_match else None

    # Parties
    claimant_name = lv(["Claimant Name", "Claimant", "CLAIMANT"])
    claimant_contact = lv(["Claimant Contact", "Contact"])

    # Collect third parties
    third_parties = []
    tp_matches = re.findall(r"Third Part[yi][:\s]+([^\n]+)", t, re.IGNORECASE)
    third_parties = [m.strip() for m in tp_matches if m.strip()]

    # Witnesses
    witness_matches = re.findall(r"Witness[:\s]+([^\n]+)", t, re.IGNORECASE)
    witnesses = [m.strip() for m in witness_matches if m.strip()]

    # Asset
    asset_type = lv(["Asset Type", "ASSET TYPE"])
    asset_id = lv(["Asset ID", "V.I.N.", "VIN", "VIN:", "Building ID", "License Plate"])
    asset_description = lv(["Year / Make / Model", "Make", "Model"])
    damage_description = lv(["Damage Description", "DESCRIBE DAMAGE", "Damage:"])
    estimated_damage_raw = lv(["Estimated Damage Amount", "Estimate Amount", "ESTIMATE AMOUNT"])
    estimated_damage_amount = _parse_amount(estimated_damage_raw)

    # Mandatory
    claim_type_raw = lv(["Claim Type", "CLAIM TYPE", "Line of Business"])
    # Normalise
    claim_type = "Other"
    if claim_type_raw:
        low = claim_type_raw.lower()
        if "injur" in low or "bodily" in low:
            claim_type = "Injury"
        elif "fire" in low:
            claim_type = "Fire"
        elif "theft" in low or "stolen" in low:
            claim_type = "Theft"
        elif "property" in low or "damage" in low or "collision" in low or "water" in low:
            claim_type = "Property Damage"
        else:
            claim_type = claim_type_raw

    attachments_raw = lv(["Attachments", "ATTACHMENTS"])
    attachments = [a.strip() for a in attachments_raw.split(",")] if attachments_raw else []

    initial_estimate_raw = lv(["Initial Estimate", "INITIAL ESTIMATE"])
    initial_estimate = _parse_amount(initial_estimate_raw)

    return {
        "policy_number": policy_number,
        "policyholder_name": policyholder_name,
        "effective_date": effective_date,
        "expiry_date": expiry_date,
        "carrier": carrier,
        "date_of_loss": date_of_loss,
        "time_of_loss": time_of_loss,
        "location_of_loss": location_of_loss,
        "incident_description": incident_description,
        "police_report_number": police_report,
        "claimant_name": claimant_name,
        "claimant_contact": claimant_contact,
        "third_parties": third_parties,
        "witnesses": witnesses,
        "asset_type": asset_type,
        "asset_id": asset_id,
        "asset_description": asset_description,
        "damage_description": damage_description,
        "estimated_damage_amount": estimated_damage_amount,
        "claim_type": claim_type,
        "attachments": attachments,
        "initial_estimate": initial_estimate,
    }


def extract_fields(fnol_text: str, use_ai: bool = True, api_key: Optional[str] = None) -> dict:
    
    if use_ai and _ANTHROPIC_AVAILABLE:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if key:
            try:
                return extract_with_claude(fnol_text, api_key=key)
            except Exception as e:
                print(f"  [⚠]  Claude API extraction failed ({e}); falling back to regex.")

    return extract_with_regex(fnol_text)
