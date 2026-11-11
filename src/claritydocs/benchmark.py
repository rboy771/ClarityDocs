import json
from datetime import timedelta
from pathlib import Path
from typing import List, Dict, Any
from claritydocs.dates import extract_letter_date
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
    total_matched_evidence = 0
    total_false_positives = 0

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

        # 2. Evidence match: recall (expected rules found) and precision (no unexpected rules)
        expected_items = set(case["expected"]["expected_evidence"])
        matched_items = set(item.item_name for item in report.evidence_checklist)
        found_in_case = len(expected_items.intersection(matched_items))
        extra_items = matched_items - expected_items
        total_expected_evidence += len(expected_items)
        retrieved_expected_evidence += found_in_case
        total_matched_evidence += len(matched_items)
        total_false_positives += len(extra_items)
        evidence_ok = (found_in_case == len(expected_items)) and not extra_items

        # 3. Deadline match: the calculated due date must equal letter date + expected window
        letter_date = extract_letter_date(case["text"])
        expected_due = (
            (letter_date + timedelta(days=case["expected"]["expected_days"])).isoformat()
            if letter_date else None
        )
        deadline_ok = expected_due is not None and any(d.due_date == expected_due for d in report.deadlines)
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
        extra_note = f" | EXTRA: {sorted(extra_items)}" if extra_items else ""
        print(f"[{status_str:4}] {case['id']:<35} | Cat: {case['category']:<22} | Evidence: {found_in_case}/{len(expected_items)}{extra_note}")

    recall_rate = (retrieved_expected_evidence / total_expected_evidence) * 100
    precision_rate = ((total_matched_evidence - total_false_positives) / max(1, total_matched_evidence)) * 100
    deadline_accuracy = (accurate_deadlines / total_expected_deadlines) * 100
    overall_accuracy = (passed_cases / total_cases) * 100
    privacy_coverage = (performed_redactions / max(1, total_expected_redactions)) * 100

    print("--------------------------------------------------------------------------------")
    print(f"Total Benchmark Cases Evaluated  : {total_cases}")
    print(f"Overall End-to-End Test Pass Rate: {overall_accuracy:.1f}% ({passed_cases}/{total_cases})")
    print(f"Statutory Evidence Recall        : {recall_rate:.1f}% ({retrieved_expected_evidence}/{total_expected_evidence})")
    print(f"Statutory Evidence Precision     : {precision_rate:.1f}% ({total_matched_evidence - total_false_positives}/{total_matched_evidence})")
    print(f"Due Date Accuracy                : {deadline_accuracy:.1f}% ({accurate_deadlines}/{total_expected_deadlines})")
    print(f"Privacy PII Redaction Coverage   : {privacy_coverage:.1f}% ({performed_redactions}/{total_expected_redactions})")
    print("================================================================================")

    return overall_accuracy, recall_rate, deadline_accuracy, privacy_coverage


if __name__ == "__main__":
    run_benchmark()
