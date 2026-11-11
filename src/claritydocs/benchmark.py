import json
from pathlib import Path
from typing import List, Dict, Any
from claritydocs.matcher import StatutoryRuleMatcher
from claritydocs.sanitizer import LocalPrivacySanitizer

DATA_PATH = Path(__file__).resolve().parent / "data" / "benchmark_cases.json"


def load_benchmark_cases() -> List[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_benchmark():
    cases = load_benchmark_cases()
    sanitizer = LocalPrivacySanitizer()
    matcher = StatutoryRuleMatcher()

    total_cases = len(cases)
    passed_cases = 0

    total_expected_evidence = 0
    retrieved_expected_evidence = 0

    total_expected_deadlines = total_cases
    accurate_deadlines = 0

    total_expected_redactions = 0
    performed_redactions = 0

    print("================================================================================")
    print("           CLARITYDOCS 25-CASE STATUTORY & PRIVACY BENCHMARK HARNESS            ")
    print("================================================================================")

    for case in cases:
        clean_text, redactions = sanitizer.sanitize(case["text"])
        report = matcher.analyze_and_match(clean_text, len(redactions))

        # 1. Authority match
        authority_ok = (report.issuing_body == case["expected"]["issuing_body"])

        # 2. Evidence match
        expected_items = set(case["expected"]["expected_evidence"])
        matched_items = set(item.item_name for item in report.evidence_checklist)
        found_in_case = len(expected_items.intersection(matched_items))
        total_expected_evidence += len(expected_items)
        retrieved_expected_evidence += found_in_case
        evidence_ok = (found_in_case == len(expected_items))

        # 3. Deadline match
        deadline_ok = any(d.days_remaining is not None for d in report.deadlines)
        if deadline_ok:
            accurate_deadlines += 1

        # 4. Redactions
        min_red = case["expected"]["min_redactions"]
        total_expected_redactions += min_red
        performed_redactions += min(len(redactions), min_red)
        redactions_ok = (len(redactions) >= min_red)

        case_passed = authority_ok and evidence_ok and deadline_ok and redactions_ok
        if case_passed:
            passed_cases += 1

        status_str = "PASS" if case_passed else "FAIL"
        print(f"[{status_str:4}] {case['id']:<35} | Cat: {case['category']:<22} | Evidence: {found_in_case}/{len(expected_items)}")

    recall_rate = (retrieved_expected_evidence / total_expected_evidence) * 100
    deadline_accuracy = (accurate_deadlines / total_expected_deadlines) * 100
    overall_accuracy = (passed_cases / total_cases) * 100
    privacy_coverage = (performed_redactions / max(1, total_expected_redactions)) * 100

    print("--------------------------------------------------------------------------------")
    print(f"Total Benchmark Cases Evaluated  : {total_cases}")
    print(f"Overall End-to-End Test Pass Rate: {overall_accuracy:.1f}% ({passed_cases}/{total_cases})")
    print(f"Statutory Evidence Recall (BM25) : {recall_rate:.1f}% ({retrieved_expected_evidence}/{total_expected_evidence})")
    print(f"Deadline Calculation Accuracy    : {deadline_accuracy:.1f}% ({accurate_deadlines}/{total_expected_deadlines})")
    print(f"Privacy PII Redaction Coverage   : {privacy_coverage:.1f}% ({performed_redactions}/{total_expected_redactions})")
    print("================================================================================")

    return overall_accuracy, recall_rate, deadline_accuracy, privacy_coverage


if __name__ == "__main__":
    run_benchmark()
