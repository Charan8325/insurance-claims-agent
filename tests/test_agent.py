
import json
import os
import sys
import unittest

# ── Path setup ───────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, ROOT)

from validator import validate, find_missing_fields, find_inconsistencies
from router import route_claim, ROUTE_FAST_TRACK, ROUTE_MANUAL_REVIEW, ROUTE_INVESTIGATION, ROUTE_SPECIALIST


# ────────────────────────────────────────────────────────────────────────────
# Helper: build a minimal complete extracted dict
# ────────────────────────────────────────────────────────────────────────────

def _complete_extraction(**overrides):
    base = {
        "policy_number": "POL-12345",
        "policyholder_name": "John Doe",
        "effective_date": "01/01/2024",
        "expiry_date": "12/31/2024",
        "carrier": "TestCo Insurance",
        "date_of_loss": "03/15/2024",
        "time_of_loss": "08:45 AM",
        "location_of_loss": "123 Main St, Springfield, IL",
        "incident_description": "Vehicle rear-ended at a stop light.",
        "police_report_number": "SP-2024-001",
        "claimant_name": "John Doe",
        "claimant_contact": "(555) 555-0101",
        "third_parties": ["Jane Smith"],
        "witnesses": [],
        "asset_type": "Vehicle",
        "asset_id": "1HGCV1F30KA000001",
        "asset_description": "2020 Honda Accord",
        "damage_description": "Rear bumper damage",
        "estimated_damage_amount": 5000,
        "claim_type": "Property Damage",
        "attachments": ["Police Report", "Photos"],
        "initial_estimate": 5000,
    }
    base.update(overrides)
    return base


class TestValidator(unittest.TestCase):

    def test_complete_form_has_no_missing_fields(self):
        ext = _complete_extraction()
        missing = find_missing_fields(ext)
        self.assertEqual(missing, [], f"Unexpected missing fields: {missing}")

    def test_missing_policy_number_detected(self):
        ext = _complete_extraction(policy_number=None)
        missing = find_missing_fields(ext)
        self.assertIn("policy_number", missing)

    def test_missing_claimant_contact_detected(self):
        ext = _complete_extraction(claimant_contact=None)
        missing = find_missing_fields(ext)
        self.assertIn("claimant_contact", missing)

    def test_is_complete_true_when_all_mandatory_present(self):
        result = validate(_complete_extraction())
        self.assertTrue(result["is_complete"])

    def test_is_complete_false_when_field_missing(self):
        result = validate(_complete_extraction(date_of_loss=None))
        self.assertFalse(result["is_complete"])

    def test_inconsistency_detected_on_damage_mismatch(self):
        # 5000 damage but 20000 estimate → >20% deviation
        ext = _complete_extraction(estimated_damage_amount=5000, initial_estimate=20000)
        issues = find_inconsistencies(ext)
        self.assertTrue(len(issues) > 0, "Should detect amount mismatch")

    def test_no_inconsistency_on_matching_amounts(self):
        ext = _complete_extraction(estimated_damage_amount=5000, initial_estimate=5100)
        issues = find_inconsistencies(ext)
        self.assertEqual(issues, [])

    def test_injury_claim_type_mismatch_detected(self):
        # Description mentions injury but type is Property Damage
        ext = _complete_extraction(
            incident_description="Driver sustained serious injuries in the crash.",
            claim_type="Property Damage"
        )
        issues = find_inconsistencies(ext)
        self.assertTrue(any("injury" in i.lower() for i in issues))


# ────────────────────────────────────────────────────────────────────────────
# Router tests
# ────────────────────────────────────────────────────────────────────────────

class TestRouter(unittest.TestCase):

    def _route(self, **overrides):
        ext = _complete_extraction(**overrides)
        val = validate(ext)
        return route_claim(ext, val)

    def test_fast_track_for_low_damage_complete_form(self):
        result = self._route(estimated_damage_amount=8500)
        self.assertEqual(result["recommended_route"], ROUTE_FAST_TRACK)

    def test_manual_review_for_missing_fields(self):
        result = self._route(claimant_contact=None, date_of_loss=None)
        self.assertEqual(result["recommended_route"], ROUTE_MANUAL_REVIEW)

    def test_investigation_flag_for_fraud_keyword(self):
        result = self._route(
            incident_description="The accident appears to have been staged by the claimant.",
            estimated_damage_amount=10000,
        )
        self.assertEqual(result["recommended_route"], ROUTE_INVESTIGATION)

    def test_investigation_flag_for_inconsistent_keyword(self):
        result = self._route(
            incident_description="Claimant's account is inconsistent with physical evidence.",
            estimated_damage_amount=12000,
        )
        self.assertEqual(result["recommended_route"], ROUTE_INVESTIGATION)

    def test_specialist_queue_for_injury_claim(self):
        result = self._route(
            claim_type="Injury",
            incident_description="Driver suffered broken arm and concussion.",
            estimated_damage_amount=4000,
        )
        self.assertEqual(result["recommended_route"], ROUTE_SPECIALIST)

    def test_manual_review_for_high_damage(self):
        result = self._route(estimated_damage_amount=285000)
        self.assertEqual(result["recommended_route"], ROUTE_MANUAL_REVIEW)

    def test_manual_review_when_amount_unknown(self):
        result = self._route(estimated_damage_amount=None, initial_estimate=None)
        self.assertEqual(result["recommended_route"], ROUTE_MANUAL_REVIEW)

    def test_reasoning_is_non_empty(self):
        result = self._route(estimated_damage_amount=5000)
        self.assertTrue(len(result["reasoning"]) > 0)

    def test_fraud_flag_appears_in_flags_list(self):
        result = self._route(
            incident_description="This looks like a case of fraud.",
            estimated_damage_amount=5000,
        )
        self.assertIn("Investigation Flag", result["flags"])


class TestIntegration(unittest.TestCase):

    FNOL_DIR = os.path.join(ROOT, "fnol_docs")
    OUTPUT_DIR = os.path.join(ROOT, "output", "test_run")

    def _process(self, filename: str) -> dict:
        from agent import process_claim
        pdf_path = os.path.join(self.FNOL_DIR, filename)
        if not os.path.exists(pdf_path):
            self.skipTest(f"Test PDF not found: {filename}")
        return process_claim(pdf_path, use_ai=False)

    def test_fnol_001_routes_fast_track(self):
        result = self._process("fnol_001_fasttrack.pdf")
        self.assertEqual(result["recommendedRoute"], ROUTE_FAST_TRACK)

    def test_fnol_002_routes_manual_review(self):
        result = self._process("fnol_002_missing_fields.pdf")
        self.assertEqual(result["recommendedRoute"], ROUTE_MANUAL_REVIEW)
        self.assertTrue(len(result["missingFields"]) > 0)

    def test_fnol_003_routes_specialist(self):
        result = self._process("fnol_003_injury.pdf")
        self.assertEqual(result["recommendedRoute"], ROUTE_SPECIALIST)

    def test_fnol_004_routes_investigation(self):
        result = self._process("fnol_004_fraud_flag.pdf")
        self.assertEqual(result["recommendedRoute"], ROUTE_INVESTIGATION)

    def test_fnol_005_routes_manual_review_high_damage(self):
        result = self._process("fnol_005_large_damage.pdf")
        self.assertEqual(result["recommendedRoute"], ROUTE_MANUAL_REVIEW)

    def test_output_has_required_keys(self):
        result = self._process("fnol_001_fasttrack.pdf")
        for key in ("extractedFields", "missingFields", "recommendedRoute", "reasoning"):
            self.assertIn(key, result, f"Missing required key: {key}")

    def test_extracted_fields_policy_number(self):
        result = self._process("fnol_001_fasttrack.pdf")
        pn = result["extractedFields"].get("policy_number")
        self.assertIsNotNone(pn, "Policy number should be extracted")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestBlankFormDetection(unittest.TestCase):
    """Fix 1: blank / template PDFs should be detected and routed to Manual Review."""

    def test_blank_acord_detected_as_blank(self):
        from validator import is_blank_form
        blank_extraction = {
            "policy_number": "CONTACT",
            "policyholder_name": "(First, Middle, Last) INSURED'S MAILING ADDRESS",
            "effective_date": None,
            "expiry_date": None,
            "carrier": "NAIC CODE",
            "date_of_loss": "AND TIME AM",
            "time_of_loss": None,
            "location_of_loss": "POLICE OR FIRE DEPARTMENT CONTACTED",
            "incident_description": "(ACORD 101, Additional Remarks Schedule, may be attached)",
            "police_report_number": "COUNTRY:",
            "claimant_name": "for the purpose of defrauding",
            "claimant_contact": "NAME:",
            "third_parties": [],
            "witnesses": [],
            "asset_type": None,
            "asset_id": "OWNER'S NAME AND ADDRESS (Check if same as insured)",
            "asset_description": "BODY TYPE: PLATE NUMBER STATE",
            "damage_description": "Y / N",
            "estimated_damage_amount": None,
            "claim_type": "(A/C, No, Ext):",
            "attachments": [],
            "initial_estimate": None,
        }
        self.assertTrue(is_blank_form(blank_extraction))

    def test_real_fnol_not_detected_as_blank(self):
        from validator import is_blank_form
        self.assertFalse(is_blank_form(_complete_extraction()))

    def test_blank_acord_integration(self):
        from agent import process_claim
        pdf_path = os.path.join(ROOT, "fnol_docs", "acord_auto_loss.pdf")
        if not os.path.exists(pdf_path):
            self.skipTest("ACORD blank form not found")
        result = process_claim(pdf_path, use_ai=False)
        self.assertEqual(result["recommendedRoute"], ROUTE_MANUAL_REVIEW)
        self.assertTrue(result["_metadata"]["is_blank_form"])
        self.assertIn("Blank/Template Form", result["_metadata"]["flags"][0])


class TestNegatedInjury(unittest.TestCase):
    """Fix 2 & 3: 'No injuries' in description must NOT trigger injury inconsistency."""

    def test_no_injuries_reported_is_not_flagged(self):
        from validator import find_inconsistencies
        ext = _complete_extraction(
            incident_description="Vehicle rear-ended at a stop light. No injuries were reported.",
            claim_type="Property Damage",
        )
        issues = find_inconsistencies(ext)
        self.assertFalse(
            any("injury" in i.lower() for i in issues),
            f"Should NOT flag negated injury mention. Got: {issues}"
        )

    def test_no_injuries_variant_not_flagged(self):
        from validator import find_inconsistencies
        ext = _complete_extraction(
            incident_description="Fire in the warehouse. No injuries. Cause: faulty wiring.",
            claim_type="Fire",
        )
        issues = find_inconsistencies(ext)
        self.assertFalse(any("injury" in i.lower() for i in issues))

    def test_real_injury_still_flagged(self):
        from validator import find_inconsistencies
        ext = _complete_extraction(
            incident_description="Driver suffered a broken arm and concussion.",
            claim_type="Property Damage",
        )
        issues = find_inconsistencies(ext)
        self.assertTrue(any("injury" in i.lower() for i in issues))

    def test_fnol_001_no_false_injury_flag(self):
        from agent import process_claim
        pdf_path = os.path.join(ROOT, "fnol_docs", "fnol_001_fasttrack.pdf")
        if not os.path.exists(pdf_path):
            self.skipTest("FNOL 001 not found")
        result = process_claim(pdf_path, use_ai=False)
        issues = result["_metadata"]["inconsistencies"]
        self.assertFalse(
            any("injury" in i.lower() for i in issues),
            f"FNOL 001 should not have injury inconsistency flag. Got: {issues}"
        )

    def test_fnol_005_no_false_injury_flag(self):
        from agent import process_claim
        pdf_path = os.path.join(ROOT, "fnol_docs", "fnol_005_large_damage.pdf")
        if not os.path.exists(pdf_path):
            self.skipTest("FNOL 005 not found")
        result = process_claim(pdf_path, use_ai=False)
        issues = result["_metadata"]["inconsistencies"]
        self.assertFalse(
            any("injury" in i.lower() for i in issues),
            f"FNOL 005 should not have injury inconsistency flag. Got: {issues}"
        )
