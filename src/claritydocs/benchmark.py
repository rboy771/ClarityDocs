import json
from typing import List, Dict, Any
from claritydocs.matcher import StatutoryRuleMatcher
from claritydocs.sanitizer import LocalPrivacySanitizer

BENCHMARK_CASES: List[Dict[str, Any]] = [
    {
        "id": "case_01_ukvi_further_evidence",
        "text": """
        Home Office - UK Visas and Immigration
        Case Ref: GWF098765432
        Applicant NI: AB123456C
        
        We need more information to assess your application for Leave to Remain.
        Please provide your bank statement showing adequate maintenance funds for the last 28 days.
        Also include your Tuberculosis (TB) certificate from an authorized testing centre.
        
        You have 14 days from the date of this letter to provide these documents.
        """,
        "expected": {
            "issuing_body": "UK Visas and Immigration (Home Office)",
            "expected_evidence": ["Bank Statements & Financial Proof", "Tuberculosis (TB) Certificate"],
            "expected_days": 14,
            "min_redactions": 2
        }
    },
    {
        "id": "case_02_dwp_pip_decision",
        "text": """
        Department for Work and Pensions (DWP)
        Personal Independence Payment (PIP) Decision
        National Insurance: CD654321D
        
        We have looked at your claim again. You scored 0 points for daily living activities.
        If you disagree with this decision, you can ask for a mandatory reconsideration.
        You must write to us within one calendar month of the date of this letter.
        """,
        "expected": {
            "issuing_body": "Department for Work and Pensions (DWP)",
            "expected_evidence": ["Mandatory Reconsideration Request (DWP)"],
            "expected_days": 30,
            "min_redactions": 1
        }
    },
    {
        "id": "case_03_spouse_visa_accommodation",
        "text": """
        UK Visas and Immigration
        We require proof of adequate accommodation for your spouse visa application.
        Provide a signed tenancy agreement or letter from your landlord confirming permission to reside.
        Ensure you also supply proof of English language proficiency at level B1.
        Submit your documents within 28 days.
        """,
        "expected": {
            "issuing_body": "UK Visas and Immigration (Home Office)",
            "expected_evidence": ["Adequate Accommodation Evidence", "Proof of English Language Proficiency"],
            "expected_days": 28,
            "min_redactions": 0
        }
    }
]


def run_benchmark():
    sanitizer = LocalPrivacySanitizer()
    matcher = StatutoryRuleMatcher()

    total_cases = len(BENCHMARK_CASES)
    passed_cases = 0
    total_expected_evidence = 0
    retrieved_expected_evidence = 0

    print("==================================================")
    print("      ClarityDocs Statutory Benchmark Suite       ")
    print("==================================================")

    for case in BENCHMARK_CASES:
        clean_text, redactions = sanitizer.sanitize(case["text"])
        report = matcher.analyze_and_match(clean_text, len(redactions))

        # Check evidence recall
        expected_items = set(case["expected"]["expected_evidence"])
        matched_items = set(item.item_name for item in report.evidence_checklist)
        
        total_expected_evidence += len(expected_items)
        found_in_case = len(expected_items.intersection(matched_items))
        retrieved_expected_evidence += found_in_case

        # Check deadline accuracy
        deadline_matches = any(d.days_remaining == case["expected"]["expected_days"] for d in report.deadlines)

        case_passed = (found_in_case == len(expected_items)) and deadline_matches
        if case_passed:
            passed_cases += 1

        print(f"[{'PASS' if case_passed else 'FAIL'}] {case['id']}")
        print(f"       - Issuing Body: {report.issuing_body}")
        print(f"       - Redactions: {len(redactions)} (Expected >= {case['expected']['min_redactions']})")
        print(f"       - Evidence Recall: {found_in_case}/{len(expected_items)}")

    recall_rate = (retrieved_expected_evidence / total_expected_evidence) * 100
    accuracy = (passed_cases / total_cases) * 100

    print("--------------------------------------------------")
    print(f"Overall Test Accuracy: {accuracy:.1f}% ({passed_cases}/{total_cases})")
    print(f"Statutory Evidence Recall: {recall_rate:.1f}% ({retrieved_expected_evidence}/{total_expected_evidence})")
    print("==================================================")


if __name__ == "__main__":
    run_benchmark()
