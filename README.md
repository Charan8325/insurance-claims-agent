# 🛡️ AI-Powered Insurance FNOL Processing Agent

An autonomous end-to-end pipeline for processing **First Notice of Loss (FNOL)** insurance claims. Upload a PDF form and the agent extracts structured data using Claude AI (with a seamless regex fallback), validates every field, detects inconsistencies, and routes the claim to the correct workflow — all in one command.

Includes both a **CLI** for batch processing and a **Flask web UI** deployable on Render.

---

## ✨ Features

- **PDF Extraction** — Parses FNOL forms with layout preservation via `pdfplumber`, handles multi-page documents
- **AI-Powered Field Extraction** — Uses `claude-opus-4-5` to extract structured JSON from any document layout or phrasing
- **Automatic Regex Fallback** — Silently falls back to heuristic extraction if the API key is missing or the Claude call fails
- **Blank Form Detection** — Identifies and short-circuits template/blank PDFs before routing
- **Field Validation** — Checks 14 mandatory fields and 5 recommended fields; detects logical inconsistencies (damage amount mismatch, claim type vs description conflicts)
- **Smart Claim Routing** — Priority-ordered rules assign each claim to Fast-track, Manual Review, Investigation Flag, or Specialist Queue
- **Batch Processing** — Process an entire folder of PDFs and get a combined `all_results.json`
- **Web UI** — Flask app with drag-and-drop PDF upload and JSON result display
- **Render Deployment** — `render.yaml` included for one-click cloud deployment

---

## 🏗️ Architecture

```
FNOL PDF
   │
   ▼
src/pdf_extractor.py     ← pdfplumber: raw text + tables + metadata
   │
   ▼
src/field_extractor.py   ← Claude AI (claude-opus-4-5) → regex fallback
   │
   ▼
src/validator.py         ← Missing fields · Blank form detection · Inconsistencies
   │
   ▼
src/router.py            ← Priority routing rules → Fast-track / Manual Review /
   │                        Investigation Flag / Specialist Queue
   ▼
JSON Output  +  Flask Web UI (app.py)
```

---

## 📁 Project Structure

```
insurance-claims-agent/
├── agent.py                        # Main orchestrator + CLI entry point
├── app.py                          # Flask web application
├── generate_dummy_fnols.py         # Script to create 5 test FNOL PDFs
├── requirements.txt
├── Procfile                        # gunicorn start command for deployment
├── render.yaml                     # Render.com deployment config
├── README.md
│
├── fnol_docs/                      # Sample input PDFs
│   ├── fnol_001_fasttrack.pdf      # Complete claim, damage < $25k
│   ├── fnol_002_missing_fields.pdf # Incomplete submission
│   ├── fnol_003_injury.pdf         # Injury claim → Specialist Queue
│   ├── fnol_004_fraud_flag.pdf     # Fraud keywords → Investigation
│   ├── fnol_005_large_damage.pdf   # Damage ≥ $25k → Manual Review
│   └── acord_auto_loss.pdf         # Real ACORD 2 blank template
│
├── src/
│   ├── pdf_extractor.py            # PDF → raw text, tables, metadata
│   ├── field_extractor.py          # Structured field extraction (AI + regex)
│   ├── validator.py                # Validation and blank-form detection
│   └── router.py                   # Routing logic
│
├── templates/
│   └── index.html                  # Flask web UI
│
├── tests/
│   └── test_agent.py               # Unit + integration tests (unittest)
│
└── output/                         # JSON results (auto-created on first run)
    └── fnol_001_fasttrack_result.json
```

---

## 🚦 Routing Rules

Rules are evaluated in **priority order** — higher priority wins. An Investigation Flag is always recorded as a supplementary flag even when another primary route is assigned.

| Priority | Route | Condition |
|----------|-------|-----------|
| **1 (highest)** | **Specialist Queue** | `claim_type` contains: `injury`, `bodily`, `medical`, or `liability` |
| **2** | **Investigation Flag** | Incident/damage description contains fraud keywords: `fraud`, `fraudulent`, `inconsistent`, `staged`, `fabricated`, `false claim`, `fake`, `suspicious` |
| **3** | **Manual Review** | Any of the 14 mandatory fields is missing |
| **4 (default)** | **Fast-track** | Damage `< $25,000`, all mandatory fields present, no fraud indicators |
| — | **Manual Review** | Damage `≥ $25,000` or damage amount could not be determined |

**Blank forms** short-circuit all rules and go directly to Manual Review with a `"Blank/Template Form"` flag.

---

## 📋 Extracted Fields

### Mandatory (14 fields — absence triggers Manual Review)

| Field | Description |
|-------|-------------|
| `policy_number` | Policy identifier |
| `policyholder_name` | Name of the insured |
| `effective_date` | Policy start date |
| `expiry_date` | Policy end date |
| `date_of_loss` | Date of the incident |
| `location_of_loss` | Where the incident occurred |
| `incident_description` | Narrative of what happened |
| `claimant_name` | Person filing the claim |
| `claimant_contact` | Phone / email of claimant |
| `asset_type` | Type of asset (vehicle, property, etc.) |
| `damage_description` | Description of damage sustained |
| `estimated_damage_amount` | Numeric damage estimate (USD) |
| `claim_type` | One of: `Property Damage`, `Injury`, `Theft`, `Fire`, `Other` |
| `initial_estimate` | Initial repair/settlement estimate (USD) |

### Recommended (5 fields — absence is noted but does not block routing)

`carrier` · `time_of_loss` · `asset_id` (VIN / address) · `attachments` · `police_report_number`

### Additional extracted fields

`asset_description` · `third_parties` (list) · `witnesses` (list)

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Charan8325/insurance-claims-agent.git
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

> Without this, the agent automatically and silently falls back to regex-based extraction — no configuration needed.

---

## 🚀 Usage

### Generate the test FNOL documents (first-time setup)

```bash
python generate_dummy_fnols.py
```

This creates 5 PDF test cases in `fnol_docs/`, each exercising a different routing scenario.

---

### CLI — Process a single FNOL PDF

```bash
# AI extraction (requires ANTHROPIC_API_KEY)
python agent.py fnol_docs/fnol_001_fasttrack.pdf

# Regex-only mode — no API key needed
python agent.py fnol_docs/fnol_001_fasttrack.pdf --no-ai

# Pretty-print JSON result to terminal
python agent.py fnol_docs/fnol_003_injury.pdf --no-ai --pretty

# Specify output directory
python agent.py fnol_docs/fnol_004_fraud_flag.pdf --output results/

# Pass API key inline
python agent.py fnol_docs/fnol_001_fasttrack.pdf --api-key sk-ant-...
```

### CLI — Batch process a directory

```bash
python agent.py fnol_docs/ --batch --output output/
```

Processes every `.pdf` in the folder. Saves individual `<stem>_result.json` files plus a combined `all_results.json`.

---

### Web UI — Flask app

```bash
python app.py
# → http://127.0.0.1:5000
```

Upload any FNOL PDF via the browser. The result is displayed as formatted JSON on the same page.

> **Note:** The web UI currently uses `--no-ai` (regex-only) mode. To enable AI extraction, set `ANTHROPIC_API_KEY` in your environment and update `use_ai=True` in `app.py`.

---

## ☁️ Deploy to Render

The repo includes a `render.yaml` for zero-config deployment:

1. Push to GitHub
2. Connect the repo in [Render](https://render.com)
3. Add your `ANTHROPIC_API_KEY` as an environment variable in the Render dashboard
4. Deploy — Render will run `pip install -r requirements.txt` and start with `gunicorn app:app`

---

## 📄 Output Format

Each processed claim produces a JSON file:

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
    "incident_description": "Insured vehicle was rear-ended by a red pickup truck...",
    "police_report_number": null,
    "claimant_name": "James A. Whitfield",
    "claimant_contact": "(305) 555-0192 | james.whitfield@email.com",
    "third_parties": ["Name: Robert L. Chen", "Contact: (305) 555-0847"],
    "witnesses": [],
    "asset_type": "Vehicle – Personal Automobile",
    "asset_id": "4T1BF1FK5MU123456",
    "asset_description": "2021 Toyota Camry SE",
    "damage_description": "Rear bumper crushed, trunk damage, broken tail",
    "estimated_damage_amount": 8500.0,
    "claim_type": "Property Damage",
    "attachments": ["Police Report #MDP-2024-33891", "Photos (6 images)"],
    "initial_estimate": 8500.0
  },
  "missingFields": [],
  "recommendedRoute": "Fast-track",
  "reasoning": "Estimated damage ($8,500) is below the $25,000 fast-track threshold and all mandatory fields are present with no fraud indicators. Eligible for automated fast-track settlement.",
  "_metadata": {
    "file": "fnol_001_fasttrack.pdf",
    "processed_at": "2026-05-14T10:29:23.705867+00:00",
    "extraction_method": "Claude AI",
    "is_blank_form": false,
    "recommended_missing_fields": ["police_report_number"],
    "inconsistencies": [],
    "flags": []
  }
}
```

---

## 🧪 Running Tests

```bash
# Using pytest
python -m pytest tests/ -v

# Or with unittest directly
python tests/test_agent.py
```

Tests cover validator logic (missing fields, inconsistency detection, blank-form detection) and all four routing outcomes.

---

## 🔍 How It Works

1. **PDF Extraction** (`pdf_extractor.py`) — `pdfplumber` extracts text page-by-page with layout preservation, plus raw tables and file metadata (page count, size, title).

2. **Field Extraction — AI** (`field_extractor.py`) — Claude (`claude-opus-4-5`) receives the raw text (up to 12,000 chars) and returns structured JSON directly. Handles varied layouts, abbreviations, and natural language automatically.

3. **Field Extraction — Regex Fallback** — If no API key is set or the Claude call fails, a heuristic `label → value` regex parser runs instead. Claim type is normalised from free text into the standard five categories.

4. **Validation** (`validator.py`) — Checks all 14 mandatory fields for presence. Runs a blank-form detector that counts real values vs. extracted form labels. Flags logical inconsistencies: damage-vs-estimate deviation > 20%, claim type mismatches with the incident description (with negation awareness — "no injuries" is not flagged).

5. **Routing** (`router.py`) — Priority-ordered rules evaluate the validated claim and assign a single primary route plus any supplementary flags (fraud indicators, data inconsistencies).

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `anthropic` | ≥ 0.25.0 | Claude AI API client |
| `pdfplumber` | ≥ 0.10.0 | PDF text and table extraction |
| `pypdf` | ≥ 4.0.0 | PDF utilities |
| `reportlab` | ≥ 4.0.0 | Generating dummy test PDFs |
| `flask` | ≥ 3.0.0 | Web UI |
| `gunicorn` | ≥ 21.2.0 | Production WSGI server |
| `pytest` | ≥ 7.0.0 | Test framework |
| `streamlit` | ≥ 1.45.0 | (Available for alternative UI) |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change. Make sure to add or update tests for any new functionality.

---

## 📝 License

This project is open source. See [LICENSE](LICENSE) for details.
