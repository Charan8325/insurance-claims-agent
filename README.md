# AI-Powered Insurance FNOL Processing Agent

A Python agent that processes First Notice of Loss (FNOL) insurance documents end-to-end:
extracts structured data from PDF forms, detects missing or inconsistent fields,
classifies the claim, and routes it to the correct workflow.

---

## Architecture

```
FNOL PDF
   │
   ▼
src/pdf_extractor.py   ← Extract raw text (pdfplumber)
   │
   ▼
src/field_extractor.py ← Extract structured fields (Claude AI → regex fallback)
   │
   ▼
src/validator.py       ← Detect missing / inconsistent fields
   │
   ▼
src/router.py          ← Apply routing rules → Fast-track / Manual Review /
   │                      Investigation Flag / Specialist Queue
   ▼
JSON Output
```

---

## Routing Rules

| Rule | Condition | Route |
|------|-----------|-------|
| 1 | Estimated damage **< $25,000** and all fields present, no fraud indicators | **Fast-track** |
| 2 | Any **mandatory field is missing** | **Manual Review** |
| 3 | Description contains `fraud`, `inconsistent`, `staged`, etc. | **Investigation Flag** |
| 4 | Claim type = **Injury** | **Specialist Queue** |

Rules are evaluated in priority order (4 > 3 > 2 > 1).  
An Investigation Flag is always noted even when another route applies.

---

## Project Structure

```
insurance_agent/
├── agent.py                    # Main orchestrator + CLI
├── generate_dummy_fnols.py     # Script to create test FNOL PDFs
├── requirements.txt
├── README.md
├── fnol_docs/                  # Input FNOL PDFs
│   ├── fnol_001_fasttrack.pdf
│   ├── fnol_002_missing_fields.pdf
│   ├── fnol_003_injury.pdf
│   ├── fnol_004_fraud_flag.pdf
│   ├── fnol_005_large_damage.pdf
│   └── acord_auto_loss.pdf     # Real ACORD 2 form (blank template)
├── src/
│   ├── pdf_extractor.py        # PDF → raw text
│   ├── field_extractor.py      # Raw text → structured fields (AI + regex)
│   ├── validator.py            # Field validation
│   └── router.py               # Routing logic
├── tests/
│   └── test_agent.py           # Unit + integration tests
└── output/                     # JSON results (auto-created)
```

---

## Setup

### 1. Clone / download the repository

```bash
git clone https://github.com/your-username/insurance-claims-agent.git
cd insurance-claims-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. (Optional) Set your Anthropic API key for AI-powered extraction

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

Without this, the agent falls back to regex-based extraction automatically.

---

## Usage

### Generate the dummy test FNOL documents (first time)

```bash
python generate_dummy_fnols.py
```

### Process a single FNOL PDF

```bash
# With Claude AI extraction (requires ANTHROPIC_API_KEY)
python agent.py fnol_docs/fnol_001_fasttrack.pdf

# Regex-only mode (no API key needed)
python agent.py fnol_docs/fnol_001_fasttrack.pdf --no-ai

# Print result to terminal
python agent.py fnol_docs/fnol_003_injury.pdf --no-ai --pretty
```

### Process all PDFs in a directory

```bash
python agent.py fnol_docs/ --batch --output output/
```

### Provide API key inline

```bash
python agent.py fnol_docs/fnol_001_fasttrack.pdf --api-key sk-ant-...
```

---

## Output Format

```json
{
  "extractedFields": {
    "policy_number": "POL-78432-AUTO",
    "policyholder_name": "James A. Whitfield",
    "effective_date": "01/01/2024",
    "expiry_date": "12/31/2024",
    "carrier": "SafeGuard Insurance Co.",
    "date_of_loss": "03/15/2024",
    "time_of_loss": "08:45 AM",
    "location_of_loss": "I-95 Northbound, Exit 22, Miami, FL 33132",
    "incident_description": "Insured vehicle was rear-ended...",
    "claimant_name": "James A. Whitfield",
    "claimant_contact": "(305) 555-0192 | james.whitfield@email.com",
    "asset_type": "Vehicle – Personal Automobile",
    "damage_description": "Rear bumper crushed, trunk damage...",
    "estimated_damage_amount": 8500,
    "claim_type": "Property Damage",
    "attachments": ["Police Report #MDP-2024-33891", "Photos (6 images)"],
    "initial_estimate": 8500
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Estimated damage ($8,500) is below the $25,000 fast-track threshold...",
  "_metadata": {
    "file": "fnol_001_fasttrack.pdf",
    "processed_at": "2024-04-28T10:00:00Z",
    "extraction_method": "Claude AI",
    "flags": []
  }
}
```

---

## Running Tests

```bash
python -m pytest tests/ -v
# or
python tests/test_agent.py
```

---

## Approach

1. **PDF Extraction** — `pdfplumber` extracts text preserving layout; this handles both structured forms and free-text descriptions.

2. **Field Extraction (AI)** — Claude (`claude-opus-4-5`) is prompted to return structured JSON directly from raw text. This handles varied document layouts and phrasing automatically.

3. **Field Extraction (Fallback)** — A regex-based extractor parses label→value patterns for offline or keyless use.

4. **Validation** — Mandatory fields are checked against a defined list. Logical inconsistencies (e.g., damage amount vs estimate mismatch, claim type vs description mismatch) are flagged separately.

5. **Routing** — Priority-ordered rule matching assigns a single primary route plus any supplementary flags.
