# SustainOps AI

### Evidence-Driven Energy Consumption Investigation & Decision Support

SustainOps AI is an AI-assisted decision-support system designed to investigate unusual building energy consumption. It combines statistical anomaly detection, historical energy patterns, evidence scoring, and sustainability knowledge retrieval to generate transparent explanations and recommendations for human review.

**The goal: Go beyond showing an energy spike—help investigate what may explain it.**

> SustainOps AI is a research prototype. Its findings are potential explanations, not confirmed causes. Recommendations and impact estimates require human review.

## Project Overview

Building energy dashboards can identify unusual consumption, but understanding why it occurred often requires additional investigation.

SustainOps AI brings together:

* Energy anomaly detection
* Historical pattern comparison
* Evidence-supported investigation hypotheses
* Sustainability knowledge retrieval (RAG)
* Human-review recommendations
* Potential impact estimation

## Sustainable Development Goal

**SDG 7 — Affordable and Clean Energy**

The project explores how data-driven investigation can support energy awareness and more informed building energy management.

## Key Features

* **Anomaly Detection:** Identifies candidate unusual electricity consumption patterns.
* **Historical Evidence:** Compares an incident with historical observations.
* **AI-Assisted Investigation:** Organizes plausible explanations using available evidence.
* **Knowledge Retrieval:** Retrieves relevant sustainability and building-operation guidance.
* **Evidence Scoring:** Presents hypotheses with supporting and limiting evidence.
* **Recommendations:** Suggests actions for facility managers to review.
* **Impact Scenarios:** Estimates potential impact under configurable assumptions.
* **Human-in-the-Loop Review:** Records reviewer decisions and maintains an audit trail.

## System Architecture

```text
Building Energy Data
        ↓
Data Quality Checks
        ↓
Baseline & Anomaly Detection
        ↓
Incident Identification
        ↓
Historical Evidence + Knowledge Retrieval
        ↓
Evidence Scoring & Investigation
        ↓
Recommendations + Impact Scenarios
        ↓
Human Review & Audit Trail
```

## Technology Stack

* Python
* Pandas / NumPy
* Streamlit
* ChromaDB
* Retrieval-Augmented Generation (RAG)
* IBM Granite integration module (experimental; live inference not verified)

## Dataset

This prototype uses an anonymized building from the Building Data Genome Project 2 (BDG2).

The selected case study is an education building, `Eagle_education_Wesley`, with electricity and other utility meter data.

The original dataset files are not included in this repository. Place the required CSV files in the local `data/` directory before running the pipeline.

## Case Study: Incident INC-016

The prototype investigated a candidate electricity-consumption incident using historical comparisons and supporting evidence.

| Investigation Output       | Result               |
| -------------------------- | -------------------- |
| Incident                   | INC-016              |
| Historical comparison rows | 17                   |
| Investigation hypotheses   | 3                    |
| Evidence level             | Moderate             |
| Review status              | Pending human review |

The incident contains both higher- and lower-than-expected observations. Therefore, estimated impact scenarios should not be interpreted as verified energy waste or guaranteed savings.

## Evaluation

Functional validation confirmed that the integrated pipeline generated the investigation outputs and recommendations, and that the Streamlit dashboard displayed the results.

The dashboard validation covered the incident overview, investigation evidence, recommendations, impact scenarios, human-review form, and audit trail.

The clean human-review test successfully recorded a reviewer decision and audit event.

**Important:** These are functional tests, not proof of anomaly-detection accuracy or generalization. Ground-truth anomaly labels were not available for a precision, recall, or F1 evaluation.

## Project Structure

```text
SustainOpsAI/
├── app/
│   └── streamlit_app.py
├── data/                  # Local dataset files (not committed)
├── knowledge/             # Sustainability knowledge documents
├── outputs/               # Selected demo artifacts
├── src/                   # Analysis and investigation modules
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Run Locally

1. Clone the repository:

```bash
git clone https://github.com/bharathivarma08-netizen/SustainOpsAI.git
cd SustainOpsAI
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add the required BDG2 CSV files to the local `data/` directory.

5. Configure environment variables using `.env.example` if required. Never commit API keys or secrets.

6. Launch the Streamlit dashboard:

```bash
streamlit run app/streamlit_app.py
```

Some pipeline features may require local dataset files and additional configuration.

## Responsible AI & Limitations

* Detected anomalies are candidates for investigation, not confirmed faults.
* Investigation hypotheses are plausible explanations, not causal findings.
* Retrieved knowledge provides general guidance; it does not prove the cause of a specific incident.
* Impact scenarios are estimates based on assumptions, not measured savings.
* The prototype focuses on a limited case study and requires broader evaluation.
* Live IBM Granite inference has not been verified in the current setup.
* Human review is required; the system does not automatically control building equipment.

## Future Improvements

* Evaluate against labeled anomalies and additional buildings.
* Improve retrieval relevance and evidence-grounding evaluation.
* Verify and integrate live IBM Granite inference.
* Calibrate impact estimates against measured outcomes.
* Add report export and multi-building comparison.

## Author

**K. Sindhu Bharathi**
B.Tech — Computer Science & Engineering (AI)

GitHub: [bharathivarma08-netizen](https://github.com/bharathivarma08-netizen)

---

*Developed as an AI for Sustainability project exploring evidence-driven energy investigation and responsible AI-assisted decision support.*
