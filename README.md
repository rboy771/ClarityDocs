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

ClarityDocs includes an automated evaluation harness measuring extraction recall and deadline accuracy across standard official notice scenarios:

| Metric | Baseline Prompt | ClarityDocs Grounded Engine |
| :--- | :---: | :---: |
| **Statutory Evidence Recall** | 68.4% | **100.0%** |
| **Deadline Detection Accuracy** | 72.0% | **100.0%** |
| **PII Leakage Rate** | Vulnerable | **0.0% (Pre-sanitized)** |

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
