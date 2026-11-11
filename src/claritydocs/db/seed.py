import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "rules.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

INITIAL_RULES = [
    {
        "rule_id": "ukvi_finance_28day",
        "rule_name": "Bank Statements & Maintenance Funds",
        "category": "financial_evidence",
        "citation": "UKVI Appendix Finance, Paragraph FIN 2.1 to FIN 8.1",
        "description": "Must prove consecutive personal funds held for at least 28 days ending no more than 31 days prior to application date.",
        "keywords": "bank statement funds maintenance savings financial balance bank letter account closing statement cash",
        "pitfalls": json.dumps([
            "Funds dipped below mandatory minimum even for a single day in the 28-day window.",
            "Statements do not clearly display bank logo, account number, or account holder name.",
            "Ad-hoc ATM slip or mini-statement supplied instead of formal monthly statement.",
            "Statement closing date is older than 31 days before application submission date."
        ])
    },
    {
        "rule_id": "ukvi_tb_certificate",
        "rule_name": "Tuberculosis (TB) Medical Clearance",
        "category": "mandatory_document",
        "citation": "UKVI Appendix T: Tuberculosis screening",
        "description": "Valid TB test certificate issued by an approved Home Office diagnostic panel clinic.",
        "keywords": "tuberculosis tb chest x-ray medical clinic certificate health check screening",
        "pitfalls": json.dumps([
            "Clinic is not on the official UKVI approved panel list for the applicant's country.",
            "Certificate has expired beyond its 6-month validity window."
        ])
    },
    {
        "rule_id": "ukvi_english_selt",
        "rule_name": "English Language Proficiency (SELT)",
        "category": "mandatory_document",
        "citation": "UKVI Appendix English Language (EL 1.1 - EL 9.1)",
        "description": "Evidence of English proficiency at CEFR B1, B2, or C1 via an approved SELT provider or Ecctis confirmation.",
        "keywords": "english language proficiency ielts selt b1 b2 cefr languagecert pearson psi ecctis degree taught in english",
        "pitfalls": json.dumps([
            "Test was completed with a standard test rather than a UKVI-approved SELT variant.",
            "Certificate missing the Unique Reference Number (URN) required for digital caseworker verification."
        ])
    },
    {
        "rule_id": "ukvi_accommodation",
        "rule_name": "Adequate Accommodation Evidence",
        "category": "mandatory_document",
        "citation": "UKVI Immigration Rules: Part 8 & Appendix FM",
        "description": "Proof of housing ownership, tenancy agreement, or landlord authorization confirming property is not overcrowded.",
        "keywords": "accommodation tenancy landlord rent property housing lease title deed inspection report overcrowded",
        "pitfalls": json.dumps([
            "No written letter from landlord specifically authorizing the visa applicant to reside at the address.",
            "Missing property inspection report when sharing premises with non-immediate family."
        ])
    },
    {
        "rule_id": "ukvi_skilled_worker_cos",
        "rule_name": "Certificate of Sponsorship & Minimum Salary",
        "category": "mandatory_document",
        "citation": "UKVI Appendix Skilled Worker (SW 4.1 - SW 14.5)",
        "description": "Valid assigned Certificate of Sponsorship (CoS) meeting general salary thresholds and standard occupational classification (SOC) code rates.",
        "keywords": "certificate of sponsorship cos salary threshold soc code sponsor licence skilled worker employment contract",
        "pitfalls": json.dumps([
            "Offered salary does not meet the revised general salary threshold or the specific SOC going rate.",
            "CoS assigned under an expired or revoked Home Office sponsor licence."
        ])
    },
    {
        "rule_id": "dwp_mandatory_reconsideration",
        "rule_name": "DWP Mandatory Reconsideration",
        "category": "form_submission",
        "citation": "Social Security Act 1998, Section 12 & DWP Decision Making Guidance",
        "description": "Formal written dispute of a DWP benefit decision within one calendar month.",
        "keywords": "mandatory reconsideration pip dwp dispute appeal decision notice personal independence payment universal credit points",
        "pitfalls": json.dumps([
            "Request filed after the 1-calendar-month deadline without documenting official 'good cause'.",
            "General complaint submitted without targeting the specific assessment descriptor activities scored 0."
        ])
    },
    {
        "rule_id": "council_tax_reduction_hardship",
        "rule_name": "Council Tax Hardship Relief (Section 13A)",
        "category": "form_submission",
        "citation": "Local Government Finance Act 1992, Section 13A(1)(c)",
        "description": "Discretionary reduction application for households experiencing exceptional financial hardship.",
        "keywords": "council tax reduction hardship section 13a arrears bailiff local authority council recovery notice",
        "pitfalls": json.dumps([
            "Failure to include full household income and expenditure breakdown.",
            "Delaying application until a liability order or court summons has already been executed."
        ])
    },
    {
        "rule_id": "eu_settlement_scheme_euss",
        "rule_name": "EU Settlement Scheme (EUSS) Continuous Residence",
        "category": "mandatory_document",
        "citation": "UKVI Appendix EU, Annex 1 (Continuous Qualifying Period)",
        "description": "Evidence of 5 years continuous residence in the UK (with no absence exceeding 6 months in any 12-month period) to transition from pre-settled to settled status.",
        "keywords": "eu settlement scheme euss settled status pre-settled european continuous residence p60 council tax bills hmrc employment",
        "pitfalls": json.dumps([
            "Absence from the UK of more than 6 months in any 12-month period without a statutory permitted reason (e.g. serious illness, study).",
            "Submitting annual utility bills that do not cover the entire multi-year residence timeline.",
            "Missing the late application reasonable grounds criteria if applying beyond the original deadline."
        ])
    }
]


def init_db(db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    """Creates the SQLite database and populates initial FTS5 rules."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Apply schema
    with open(schema_path, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # Clear existing entries
    cursor.execute("DELETE FROM statutory_rules")

    # Insert initial rules
    for r in INITIAL_RULES:
        cursor.execute(
            """
            INSERT INTO statutory_rules (rule_id, rule_name, category, citation, description, keywords, pitfalls)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["rule_id"],
                r["rule_name"],
                r["category"],
                r["citation"],
                r["description"],
                r["keywords"],
                r["pitfalls"]
            )
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("SQLite FTS5 database initialized successfully at:", DB_PATH)
