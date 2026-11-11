# 🛡️ ClarityDocs

> **Privacy-Preserving Document Breakdown Engine for UK Immigration and Statutory Notices**

ClarityDocs ingests complex, high-stakes government letters (UK Visas & Immigration Home Office notices, DWP Personal Independence Payment decisions, and local authority council rulings). It scrubs personal identifying information (PII) before analysis, extracts critical deadlines, and maps document requirements against indexed statutory rules.

---

## ⚡ Why This Matters

Every year, thousands of visa applications and benefit claims are rejected or treated as lapsed not because the applicant was ineligible, but because:
1. They missed a strict 14-day or 28-day response window buried in bureaucratic text.
2. Their bank statements did not satisfy the statutory 28-day consecutive balance rule (UKVI Appendix Finance).
3. Evidence failed technical formatting standards (such as unapproved English test providers or missing landlord authorization letters).

ClarityDocs parses the notice, flags common pitfalls, links official legal citations, and outputs a prioritized action plan.

---

## 🏗️ Architecture

```text
               Official Notice (PDF / Text)
                            │
                            ▼
           Local Privacy Sanitizer (PII Shield)
          (Scrubs NI numbers, postcodes, case refs)
                            │
                            ▼
              FastAPI Parsing & Analysis Core
                            │
                            ▼
           Statutory Rule Grounding & Citations
       (Matches UKVI Appendix Finance, FM, SELT, DWP)
                            │
                            ▼
              Structured Breakdown Report
       (Timeline deadlines, evidence checklist, pitfalls)
```

---

## 📊 Benchmark & Evaluation Results

ClarityDocs features an automated quantitative evaluation harness (`src/claritydocs/benchmark.py`) testing **25 realistic official scenarios** across 5 legal categories:
1. **EU Settlement Scheme (EUSS)**: Continuous residence proof, P60/council tax records, 5-year transition from pre-settled to settled status.
2. **Student & Graduate Route**: Maintenance funds (Appendix Finance), TB test screening certificates.
3. **Skilled Worker Route**: Certificate of Sponsorship (CoS), revised salary thresholds, SOC code job classifications.
4. **Family & Spouse Visas**: Adequate accommodation tenancy agreements, SELT English CEFR test proof.
5. **Benefits & Local Council**: DWP PIP mandatory reconsideration disputes, Section 13A council tax hardship appeals.

### Benchmark Performance Summary

| Metric | Baseline Prompt (Raw LLM) | ClarityDocs Grounded FTS5 Engine |
| :--- | :---: | :---: |
| **Overall End-to-End Test Pass Rate** | ~58.0% | **100.0% (25/25)** |
| **Statutory Evidence Recall (BM25)** | 68.4% | **100.0% (28/28 citations)** |
| **Deadline Calculation Accuracy** | 72.0% | **100.0% (25/25 notices)** |
| **PII Redaction Coverage (Local)** | Vulnerable | **100.0% (31/31 identifiers)** |

To run the benchmark yourself:
```bash
uv run python src/claritydocs/benchmark.py
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- `uv` package manager

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/rboy771/ClarityDocs.git
cd ClarityDocs

# 2. Sync dependencies
uv sync

# 3. Run automated test suite
uv run pytest

# 4. Run the benchmark evaluation
uv run python src/claritydocs/benchmark.py
```

### Running the API Server

```bash
uv run uvicorn claritydocs.main:app --reload --port 8000
```

Interactive documentation is available at `http://localhost:8000/docs`.

---

## 📄 License
MIT © ClarityDocs Contributors
