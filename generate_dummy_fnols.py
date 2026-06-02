

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "fnol_docs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="FieldLabel", fontSize=9, textColor=colors.grey, spaceAfter=1))
    styles.add(ParagraphStyle(name="FieldValue", fontSize=11, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="SectionHeader", fontSize=13, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#1a3a6b"), spaceBefore=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="DocTitle", fontSize=18, fontName="Helvetica-Bold",
                               textColor=colors.HexColor("#1a3a6b"), alignment=TA_CENTER, spaceAfter=16))
    return styles


def field_row(label, value, styles):
    return [
        Paragraph(label, styles["FieldLabel"]),
        Paragraph(str(value), styles["FieldValue"]),
    ]


# ─────────────────────────────────────────────
# FNOL 1 – Simple fast-track eligible claim
# ─────────────────────────────────────────────
def create_fnol_1():
    path = os.path.join(OUTPUT_DIR, "fnol_001_fasttrack.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=inch, leftMargin=inch,
                             topMargin=inch, bottomMargin=inch)
    styles = build_styles()
    story = []

    story.append(Paragraph("FIRST NOTICE OF LOSS — CLAIM FORM", styles["DocTitle"]))
    story.append(Paragraph("Claim Reference: CLM-2024-001", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Policy Information
    story.append(Paragraph("POLICY INFORMATION", styles["SectionHeader"]))
    data = [
        ["Policy Number:", "POL-78432-AUTO"],
        ["Policyholder Name:", "James A. Whitfield"],
        ["Policy Effective Date:", "01/01/2024"],
        ["Policy Expiry Date:", "12/31/2024"],
        ["Carrier:", "SafeGuard Insurance Co."],
        ["Line of Business:", "Personal Auto"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Incident Information
    story.append(Paragraph("INCIDENT INFORMATION", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage – Vehicle Collision"],
        ["Date of Loss:", "03/15/2024"],
        ["Time of Loss:", "08:45 AM"],
        ["Location of Loss:", "I-95 Northbound, Exit 22, Miami, FL 33132"],
        ["Police / Fire Contacted:", "Yes – Miami-Dade PD, Report #MDP-2024-33891"],
        ["Description of Accident:", ("Insured vehicle (2021 Toyota Camry) was rear-ended by a "
                                       "red pickup truck while stopped in traffic near Exit 22. "
                                       "The other driver admitted fault at the scene. "
                                       "No injuries were reported.")],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Involved Parties
    story.append(Paragraph("INVOLVED PARTIES", styles["SectionHeader"]))
    data = [
        ["Claimant Name:", "James A. Whitfield"],
        ["Claimant Contact:", "(305) 555-0192  |  james.whitfield@email.com"],
        ["Third Party Name:", "Robert L. Chen"],
        ["Third Party Contact:", "(305) 555-0847  |  robert.chen@email.com"],
        ["Third Party Insurance:", "StarCover Auto – Policy #SC-2024-00921"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Asset Details
    story.append(Paragraph("ASSET DETAILS", styles["SectionHeader"]))
    data = [
        ["Asset Type:", "Vehicle – Personal Automobile"],
        ["Year / Make / Model:", "2021 Toyota Camry SE"],
        ["VIN:", "4T1BF1FK5MU123456"],
        ["License Plate:", "FL-MKZ-7841"],
        ["Damage Description:", "Rear bumper crushed, trunk damage, broken tail lights."],
        ["Estimated Damage Amount:", "$8,500"],
        ["Vehicle Location:", "Whitfield Residence – 14 Ocean Drive, Miami, FL 33139"],
        ["When Can Vehicle Be Seen?:", "Any weekday after 5 PM"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Other Fields
    story.append(Paragraph("OTHER MANDATORY FIELDS", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage"],
        ["Initial Estimate:", "$8,500"],
        ["Attachments:", "Police Report #MDP-2024-33891, Photos (6 images)"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)

    doc.build(story)
    print(f"  ✓ Created: {path}")
    return path


# ─────────────────────────────────────────────
# FNOL 2 – Missing fields → Manual Review
# ─────────────────────────────────────────────
def create_fnol_2():
    path = os.path.join(OUTPUT_DIR, "fnol_002_missing_fields.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=inch, leftMargin=inch,
                             topMargin=inch, bottomMargin=inch)
    styles = build_styles()
    story = []

    story.append(Paragraph("FIRST NOTICE OF LOSS — CLAIM FORM", styles["DocTitle"]))
    story.append(Paragraph("Claim Reference: CLM-2024-002", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("POLICY INFORMATION", styles["SectionHeader"]))
    data = [
        ["Policy Number:", "POL-55821-HOME"],
        ["Policyholder Name:", "Maria T. Gonzalez"],
        # Effective dates intentionally omitted
        ["Carrier:", "BlueSky Property Insurance"],
        ["Line of Business:", "Homeowners"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INCIDENT INFORMATION", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage – Water Damage"],
        ["Date of Loss:", "04/02/2024"],
        # Time intentionally missing
        ["Location of Loss:", "789 Maple Street, Atlanta, GA 30301"],
        ["Police / Fire Contacted:", "No"],
        ["Description of Accident:", ("Burst pipe in the upstairs bathroom caused flooding that "
                                       "damaged the ceiling, walls and flooring on the ground floor.")],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INVOLVED PARTIES", styles["SectionHeader"]))
    data = [
        ["Claimant Name:", "Maria T. Gonzalez"],
        # Contact details intentionally missing
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("ASSET DETAILS", styles["SectionHeader"]))
    data = [
        ["Asset Type:", "Residential Property"],
        ["Asset ID / Address:", "789 Maple Street, Atlanta, GA 30301"],
        ["Damage Description:", "Water damage to ceiling, walls, and flooring."],
        ["Estimated Damage Amount:", "$32,000"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("OTHER MANDATORY FIELDS", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage"],
        # Initial estimate and attachments intentionally missing
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(t)

    doc.build(story)
    print(f"  ✓ Created: {path}")
    return path


# ─────────────────────────────────────────────
# FNOL 3 – Injury Claim → Specialist Queue
# ─────────────────────────────────────────────
def create_fnol_3():
    path = os.path.join(OUTPUT_DIR, "fnol_003_injury.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=inch, leftMargin=inch,
                             topMargin=inch, bottomMargin=inch)
    styles = build_styles()
    story = []

    story.append(Paragraph("FIRST NOTICE OF LOSS — CLAIM FORM", styles["DocTitle"]))
    story.append(Paragraph("Claim Reference: CLM-2024-003", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("POLICY INFORMATION", styles["SectionHeader"]))
    data = [
        ["Policy Number:", "POL-99102-LIFE"],
        ["Policyholder Name:", "David K. Okonkwo"],
        ["Policy Effective Date:", "06/01/2023"],
        ["Policy Expiry Date:", "05/31/2025"],
        ["Carrier:", "Meridian Life & Casualty"],
        ["Line of Business:", "Personal Liability / Auto"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INCIDENT INFORMATION", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Bodily Injury"],
        ["Date of Loss:", "04/10/2024"],
        ["Time of Loss:", "03:30 PM"],
        ["Location of Loss:", "Oak Street & 5th Avenue, Chicago, IL 60601"],
        ["Police / Fire Contacted:", "Yes – CPD Report #CPD-2024-10482"],
        ["Description of Accident:", ("Insured vehicle collided with a cyclist at the intersection. "
                                       "The cyclist sustained a broken collarbone and lacerations. "
                                       "Insured was turning right on green; cyclist was in the bike lane. "
                                       "Emergency services transported the injured party to Northwestern Memorial Hospital.")],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INVOLVED PARTIES", styles["SectionHeader"]))
    data = [
        ["Claimant Name:", "David K. Okonkwo"],
        ["Claimant Contact:", "(312) 555-0384  |  d.okonkwo@email.com"],
        ["Injured Party:", "Lucas Ferreira (cyclist)"],
        ["Injured Party Contact:", "(312) 555-0921  |  lucas.ferreira@email.com"],
        ["Injured Party Attorney:", "Hernandez & Associates, (312) 555-0001"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("ASSET DETAILS", styles["SectionHeader"]))
    data = [
        ["Asset Type:", "Vehicle – Personal Automobile"],
        ["Year / Make / Model:", "2019 Honda Accord EX"],
        ["VIN:", "1HGCV1F30KA012345"],
        ["License Plate:", "IL-AB-4821"],
        ["Damage Description:", "Front bumper damage, broken headlight."],
        ["Estimated Damage Amount:", "$4,200"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("OTHER MANDATORY FIELDS", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Injury"],
        ["Initial Estimate:", "$4,200 vehicle damage + medical costs TBD"],
        ["Attachments:", "Police Report #CPD-2024-10482, 4 photos, Hospital admission record"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)

    doc.build(story)
    print(f"  ✓ Created: {path}")
    return path


# ─────────────────────────────────────────────
# FNOL 4 – Fraud keywords → Investigation Flag
# ─────────────────────────────────────────────
def create_fnol_4():
    path = os.path.join(OUTPUT_DIR, "fnol_004_fraud_flag.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=inch, leftMargin=inch,
                             topMargin=inch, bottomMargin=inch)
    styles = build_styles()
    story = []

    story.append(Paragraph("FIRST NOTICE OF LOSS — CLAIM FORM", styles["DocTitle"]))
    story.append(Paragraph("Claim Reference: CLM-2024-004", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("POLICY INFORMATION", styles["SectionHeader"]))
    data = [
        ["Policy Number:", "POL-33710-AUTO"],
        ["Policyholder Name:", "Priya S. Sharma"],
        ["Policy Effective Date:", "02/01/2024"],
        ["Policy Expiry Date:", "01/31/2025"],
        ["Carrier:", "TrustShield Auto Insurance"],
        ["Line of Business:", "Commercial Auto"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INCIDENT INFORMATION", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage – Vehicle Collision"],
        ["Date of Loss:", "04/18/2024"],
        ["Time of Loss:", "11:15 PM"],
        ["Location of Loss:", "Industrial Blvd & Route 9, Newark, NJ 07102"],
        ["Police / Fire Contacted:", "Yes – Newark PD Report #NPD-2024-78231"],
        ["Description of Accident:", (
            "The claimant states her vehicle was struck from behind by an unidentified vehicle "
            "that fled the scene. However, the damage pattern is inconsistent with a rear-impact "
            "collision. A witness at the scene reported that the collision appeared staged. "
            "The claimant's account also contains inconsistent details regarding the speed and "
            "direction of the alleged other vehicle. Investigating officer noted possible fraud indicators."
        )],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INVOLVED PARTIES", styles["SectionHeader"]))
    data = [
        ["Claimant Name:", "Priya S. Sharma"],
        ["Claimant Contact:", "(973) 555-0263  |  priya.sharma@email.com"],
        ["Third Party:", "Unknown (fled scene)"],
        ["Witness:", "Mr. T. Nakamura, (973) 555-0441"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("ASSET DETAILS", styles["SectionHeader"]))
    data = [
        ["Asset Type:", "Vehicle – Commercial Van"],
        ["Year / Make / Model:", "2022 Ford Transit 250"],
        ["VIN:", "1FTBR1C80NKA55123"],
        ["License Plate:", "NJ-XTC-9910"],
        ["Damage Description:", "Rear bumper, trunk door, and rear frame damage."],
        ["Estimated Damage Amount:", "$18,700"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("OTHER MANDATORY FIELDS", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage"],
        ["Initial Estimate:", "$18,700"],
        ["Attachments:", "Police Report #NPD-2024-78231, 3 photos, Witness statement"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)

    doc.build(story)
    print(f"  ✓ Created: {path}")
    return path


# ─────────────────────────────────────────────
# FNOL 5 – Large damage, complete form
# ─────────────────────────────────────────────
def create_fnol_5():
    path = os.path.join(OUTPUT_DIR, "fnol_005_large_damage.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, rightMargin=inch, leftMargin=inch,
                             topMargin=inch, bottomMargin=inch)
    styles = build_styles()
    story = []

    story.append(Paragraph("FIRST NOTICE OF LOSS — CLAIM FORM", styles["DocTitle"]))
    story.append(Paragraph("Claim Reference: CLM-2024-005", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("POLICY INFORMATION", styles["SectionHeader"]))
    data = [
        ["Policy Number:", "POL-11204-COMM"],
        ["Policyholder Name:", "Apex Logistics LLC"],
        ["Policy Effective Date:", "01/01/2024"],
        ["Policy Expiry Date:", "12/31/2024"],
        ["Carrier:", "Continental Commercial Insurance"],
        ["Line of Business:", "Commercial Property"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INCIDENT INFORMATION", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage – Fire"],
        ["Date of Loss:", "04/22/2024"],
        ["Time of Loss:", "02:15 AM"],
        ["Location of Loss:", "4500 Commerce Parkway, Dallas, TX 75201"],
        ["Police / Fire Contacted:", "Yes – Dallas Fire Dept. Report #DFD-2024-4418"],
        ["Description of Accident:", ("Electrical fire originating in the warehouse server room "
                                       "spread to adjacent storage areas before being contained. "
                                       "Significant damage to equipment, inventory, and structural elements. "
                                       "No injuries. Cause confirmed as faulty wiring by fire investigator.")],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("INVOLVED PARTIES", styles["SectionHeader"]))
    data = [
        ["Claimant Name:", "Apex Logistics LLC (Contact: Sarah Kim, Risk Manager)"],
        ["Claimant Contact:", "(214) 555-0182  |  sarah.kim@apexlogistics.com"],
        ["Third Parties:", "None"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("ASSET DETAILS", styles["SectionHeader"]))
    data = [
        ["Asset Type:", "Commercial Property – Warehouse"],
        ["Asset ID:", "Building ID: WAR-DAL-4500"],
        ["Damage Description:", ("Server equipment total loss, 60% of inventory destroyed, "
                                  "roof damage, structural damage to east wing.")],
        ["Estimated Damage Amount:", "$285,000"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)
    story.append(Spacer(1, 10))

    story.append(Paragraph("OTHER MANDATORY FIELDS", styles["SectionHeader"]))
    data = [
        ["Claim Type:", "Property Damage"],
        ["Initial Estimate:", "$285,000"],
        ["Attachments:", "Fire Dept Report #DFD-2024-4418, Fire investigator report, 22 photos, Inventory list"],
    ]
    t = Table([[Paragraph(r[0], styles["FieldLabel"]), Paragraph(r[1], styles["FieldValue"])]
               for r in data], colWidths=[2.2 * inch, 4 * inch])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white])]))
    story.append(t)

    doc.build(story)
    print(f"  ✓ Created: {path}")
    return path


if __name__ == "__main__":
    print("Generating dummy FNOL documents...")
    create_fnol_1()
    create_fnol_2()
    create_fnol_3()
    create_fnol_4()
    create_fnol_5()
    print("\nAll dummy FNOL documents created successfully.")
