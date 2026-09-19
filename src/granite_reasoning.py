from pathlib import Path
import json
import os

from dotenv import load_dotenv

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "outputs"

INPUT_FILE = (
    OUTPUT_DIR / "INC-016_investigation.json"
)

OUTPUT_FILE = (
    OUTPUT_DIR / "INC-016_granite_report.json"
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)


API_KEY = os.getenv(
    "e5FBIOSoSq9jN1hZQkFIUx2Lf0fdYP7KhsMWagsPLJjY"
)

PROJECT_ID = os.getenv(
    "470ddc7d-510e-4bc2-9057-775718fcaf30"
)

WATSONX_URL = os.getenv(
    "WATSONX_URL",
    "https://us-south.ml.cloud.ibm.com"
)


# ============================================================
# GRANITE MODEL
# ============================================================

MODEL_ID = (
    "ibm/granite-4-h-small"
)


# ============================================================
# LOAD INVESTIGATION REPORT
# ============================================================

def load_investigation_report():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# BUILD GRANITE PROMPT
# ============================================================

def build_prompt(report):

    evidence_json = json.dumps(
        report,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are the reasoning component of SustainOps AI,
an evidence-driven building energy investigation system.

Your task is to analyze the supplied investigation evidence
and produce a transparent investigation report.

IMPORTANT RULES:

1. Do not claim that a hypothesis is a confirmed root cause.
2. Do not invent evidence.
3. Do not invent probabilities or percentages.
4. Clearly distinguish:
   - measured observations
   - historical comparisons
   - retrieved domain knowledge
   - hypotheses
   - recommendations
5. RAG knowledge provides general domain guidance.
   It is not proof that a specific event occurred.
6. Historical comparison is limited by the available
   historical observations.
7. If evidence is contradictory, explicitly mention it.
8. Recommendations are for human review.
9. Do not recommend autonomous control of building equipment.
10. Do not claim guaranteed energy or cost savings.

Analyze the incident and return JSON with exactly these fields:

{{
  "incident_summary": "",
  "key_observations": [],
  "evidence_interpretation": [],
  "plausible_hypotheses": [
    {{
      "hypothesis": "",
      "supporting_evidence": [],
      "limiting_evidence": [],
      "assessment": ""
    }}
  ],
  "recommended_next_checks": [],
  "recommendation_for_human_review": "",
  "uncertainty_and_limitations": []
}}

Keep the reasoning concise, factual and evidence-grounded.

INVESTIGATION EVIDENCE:

{evidence_json}
"""

    return prompt


# ============================================================
# CREATE GRANITE MODEL
# ============================================================

def create_granite_model():

    if not API_KEY:

        raise ValueError(
            "WATSONX_APIKEY is missing from .env"
        )

    if not PROJECT_ID:

        raise ValueError(
            "WATSONX_PROJECT_ID is missing from .env"
        )


    credentials = Credentials(
        url=WATSONX_URL,
        api_key=API_KEY
    )


    model = ModelInference(
        model_id=MODEL_ID,
        credentials=credentials,
        project_id=PROJECT_ID,
        params={
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "min_new_tokens": 100,
            "temperature": 0.2,
        }
    )

    return model


# ============================================================
# RUN GRANITE
# ============================================================

def run_granite(prompt):

    model = create_granite_model()

    response = model.generate_text(
        prompt=prompt
    )

    return response


# ============================================================
# PARSE GRANITE RESPONSE
# ============================================================

def parse_granite_response(response):

    response = response.strip()


    # Remove markdown JSON fences if Granite adds them.

    if response.startswith(
        "```json"
    ):

        response = response[
            7:
        ]

    if response.endswith(
        "```"
    ):

        response = response[
            :-3
        ]


    response = response.strip()


    try:

        return json.loads(
            response
        )

    except json.JSONDecodeError:

        return {
            "raw_response": response,
            "parsing_status": "FAILED"
        }


# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    investigation_report,
    granite_result
):

    final_report = {

        "incident": (
            investigation_report[
                "incident"
            ]
        ),

        "model": MODEL_ID,

        "reasoning_engine": "IBM Granite",

        "granite_analysis": granite_result

    }


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_report,
            file,
            indent=4,
            ensure_ascii=False
        )


    return final_report


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== SUSTAINOPS IBM GRANITE ==========\n"
    )


    # --------------------------------------------------------
    # Load evidence
    # --------------------------------------------------------

    print(
        "Loading investigation evidence..."
    )

    investigation_report = (
        load_investigation_report()
    )


    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = build_prompt(
        investigation_report
    )


    print(
        "Evidence loaded."
    )

    print(
        "Sending investigation to IBM Granite..."
    )


    # --------------------------------------------------------
    # Run Granite
    # --------------------------------------------------------

    response = run_granite(
        prompt
    )


    print(
        "\nGranite response received."
    )


    # --------------------------------------------------------
    # Parse response
    # --------------------------------------------------------

    granite_result = (
        parse_granite_response(
            response
        )
    )


    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    final_report = save_report(
        investigation_report,
        granite_result
    )


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print(
        "\n--- Granite Investigation ---\n"
    )

    print(
        json.dumps(
            granite_result,
            indent=4,
            ensure_ascii=False
        )
    )


    print(
        "\nReport saved to:"
    )

    print(
        OUTPUT_FILE
    )


    print(
        "\n=============================================\n"
    )