"""
agent.py
--------
Autonomous Insurance Claims Processing Agent.

Orchestrates the full pipeline:
  PDF → text extraction → field extraction → validation → routing → JSON output

Usage:
    python agent.py path/to/fnol.pdf [--no-ai] [--api-key KEY]

Or import and call process_claim() directly.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# ── Ensure src/ is importable when run from repo root ───────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from pdf_extractor import load_fnol_document
from field_extractor import extract_fields
from validator import validate
from router import route_claim, route_blank_form


# ────────────────────────────────────────────────────────────────────────────
# Core pipeline
# ────────────────────────────────────────────────────────────────────────────

def process_claim(
    pdf_path: str,
    use_ai: bool = True,
    api_key: str | None = None,
) -> dict:
    """
    Full FNOL processing pipeline.

    Returns a dict matching the assignment spec:
        {
            "extractedFields"  : { ... },
            "missingFields"    : [ ... ],
            "recommendedRoute" : "...",
            "reasoning"        : "...",
            "_metadata"        : { ... },
        }
    """

    print(f"\n{'='*60}")
    print(f"  Processing: {Path(pdf_path).name}")
    print(f"{'='*60}")

    # Step 1: Extract raw text from PDF
    print("  [1/4] Extracting text from PDF...")
    doc = load_fnol_document(pdf_path)
    raw_text = doc["raw_text"]
    metadata = doc["metadata"]
    print(f"        → {metadata['page_count']} page(s), {metadata['file_size_kb']} KB")

    # Step 2: Extract structured fields
    print("  [2/4] Extracting FNOL fields...")
    extraction_method = "Claude AI" if use_ai else "Regex"
    extracted = extract_fields(raw_text, use_ai=use_ai, api_key=api_key)
    print(f"        → Extraction method: {extraction_method}")

    # Step 3: Validate (includes blank-form detection)
    print("  [3/4] Validating fields...")
    validation = validate(extracted)
    n_missing = len(validation["missing_fields"])
    n_issues  = len(validation["inconsistencies"])
    is_blank  = validation.get("is_blank_form", False)
    print(f"        → Blank/template form: {is_blank}")
    print(f"        → Missing mandatory fields: {n_missing}")
    print(f"        → Inconsistencies found: {n_issues}")

    # Step 4: Route
    print("  [4/4] Routing claim...")
    if is_blank:
        routing = route_blank_form(metadata["file_name"])
    else:
        routing = route_claim(extracted, validation)
    print(f"        → Recommended route: {routing['recommended_route']}")

    output = {
        "extractedFields": extracted,
        "missingFields": validation["missing_fields"],
        "recommendedRoute": routing["recommended_route"],
        "reasoning": routing["reasoning"],
        "_metadata": {
            "file": metadata["file_name"],
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "extraction_method": extraction_method,
            "is_blank_form": is_blank,
            "recommended_missing_fields": validation["recommended_missing"],
            "inconsistencies": validation["inconsistencies"],
            "flags": routing["flags"],
        },
    }

    return output


def process_batch(
    pdf_dir: str,
    output_dir: str,
    use_ai: bool = True,
    api_key: str | None = None,
) -> list[dict]:
    """Process all PDFs in a directory and save JSON results."""
    os.makedirs(output_dir, exist_ok=True)
    pdf_paths = sorted(Path(pdf_dir).glob("*.pdf"))
    results = []

    if not pdf_paths:
        print(f"No PDF files found in: {pdf_dir}")
        return results

    print(f"\nFound {len(pdf_paths)} FNOL document(s) to process.")

    for pdf_path in pdf_paths:
        try:
            result = process_claim(str(pdf_path), use_ai=use_ai, api_key=api_key)
            results.append(result)
            stem = pdf_path.stem
            out_path = Path(output_dir) / f"{stem}_result.json"
            with open(out_path, "w") as f:
                json.dump(result, f, indent=2)
            print(f"  → Saved: {out_path}")
        except Exception as e:
            print(f"  [ERROR] Failed to process {pdf_path.name}: {e}")
            results.append({"error": str(e), "file": pdf_path.name})

    combined_path = Path(output_dir) / "all_results.json"
    with open(combined_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  ✓ Combined results saved to: {combined_path}")

    return results


# ────────────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Autonomous Insurance Claims Processing Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python agent.py fnol_docs/fnol_001_fasttrack.pdf --no-ai --pretty
  python agent.py fnol_docs/ --batch --output output/
  python agent.py fnol_docs/fnol_003_injury.pdf --api-key sk-ant-...
        """,
    )
    parser.add_argument("path", help="Path to a FNOL PDF file, or directory (with --batch).")
    parser.add_argument("--batch", action="store_true", help="Process all PDFs in directory.")
    parser.add_argument("--output", default="output", help="Directory for JSON results.")
    parser.add_argument("--no-ai", action="store_true", help="Use regex extraction only.")
    parser.add_argument("--api-key", default=None, help="Anthropic API key.")
    parser.add_argument("--pretty", action="store_true", help="Print JSON to stdout.")

    args = parser.parse_args()
    use_ai = not args.no_ai

    if args.batch:
        process_batch(args.path, args.output, use_ai=use_ai, api_key=args.api_key)
    else:
        result = process_claim(args.path, use_ai=use_ai, api_key=args.api_key)
        os.makedirs(args.output, exist_ok=True)
        stem = Path(args.path).stem
        out_path = Path(args.output) / f"{stem}_result.json"
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"\n  ✓ Result saved to: {out_path}")
        if args.pretty:
            print("\n" + json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
