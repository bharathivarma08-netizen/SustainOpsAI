from pathlib import Path
import sys
import json
import pandas as pd


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from evidence import build_evidence_package
from evidence_scoring import score_evidence


# ============================================================
# CONFIGURATION
# ============================================================

BUILDING_ID = "Eagle_education_Wesley"


# ============================================================
# INVESTIGATION AGENT
# ============================================================

class InvestigationAgent:
    """
    Tool-using investigation agent for SustainOps AI.

    The agent coordinates:
        1. Current meter evidence
        2. Historical evidence
        3. RAG evidence
        4. Evidence assessment

    It does NOT claim a confirmed root cause.
    """

    def __init__(self, building_id):

        self.building_id = building_id

        self.tools_used = []

        self.investigation_log = []


    # ========================================================
    # LOGGING
    # ========================================================

    def log(self, message):

        self.investigation_log.append(message)


    # ========================================================
    # TOOL 1 — CURRENT EVIDENCE
    # ========================================================

    def inspect_current_evidence(
        self,
        evidence_package
    ):

        self.tools_used.append(
            "current_meter_evidence"
        )

        current_evidence = (
            evidence_package[
                "current_meter_evidence"
            ]
        )

        self.log(
            "Inspected current meter behavior "
            "during the incident period."
        )

        return current_evidence


    # ========================================================
    # TOOL 2 — HISTORICAL EVIDENCE
    # ========================================================

    def inspect_historical_evidence(
        self,
        evidence_package
    ):

        self.tools_used.append(
            "historical_evidence"
        )

        historical_evidence = (
            evidence_package[
                "historical_evidence"
            ]
        )

        self.log(
            "Compared incident electricity observations "
            "with previous observations for matching "
            "month, weekday and hour."
        )

        return historical_evidence


    # ========================================================
    # TOOL 3 — RAG EVIDENCE
    # ========================================================

    def retrieve_domain_knowledge(
        self,
        evidence_package
    ):

        self.tools_used.append(
            "rag_knowledge_retrieval"
        )

        rag_evidence = (
            evidence_package[
                "rag_evidence"
            ]
        )

        self.log(
            "Retrieved sustainability knowledge relevant "
            "to possible explanations."
        )

        return rag_evidence


    # ========================================================
    # TOOL 4 — EVIDENCE ASSESSMENT
    # ========================================================

    def assess_evidence(
        self,
        evidence_package
    ):

        self.tools_used.append(
            "evidence_scoring"
        )

        assessment = score_evidence(
            evidence_package
        )

        self.log(
            "Assessed supporting and limiting evidence "
            "for possible explanations."
        )

        return assessment


    # ========================================================
    # CHECK WHETHER ENOUGH EVIDENCE EXISTS
    # ========================================================

    def check_evidence_sufficiency(
        self,
        evidence_package,
        assessment
    ):

        historical = (
            assessment[
                "historical_summary"
            ]
        )

        rag_evidence = (
            evidence_package[
                "rag_evidence"
            ]
        )

        historical_available = (
            historical["status"]
            == "AVAILABLE"
        )

        rag_available = (
            len(rag_evidence) > 0
        )

        current_available = (
            len(
                evidence_package[
                    "current_meter_evidence"
                ]
            ) > 0
        )

        enough_evidence = (
            current_available
            and historical_available
            and rag_available
        )

        if enough_evidence:

            self.log(
                "Required evidence layers are available "
                "for hypothesis generation."
            )

        else:

            self.log(
                "Evidence is incomplete; investigation "
                "should remain low-confidence."
            )

        return enough_evidence


    # ========================================================
    # GENERATE INVESTIGATION REPORT
    # ========================================================

    def generate_report(
        self,
        incident_start,
        incident_end,
        incident_id
    ):

        self.log(
            f"Investigation started for {incident_id}."
        )


        # ----------------------------------------------------
        # STEP 1 — Gather evidence
        # ----------------------------------------------------

        evidence_package = build_evidence_package(
            incident_start,
            incident_end,
            incident_id=incident_id
        )


        # ----------------------------------------------------
        # STEP 2 — Current meter evidence
        # ----------------------------------------------------

        current_evidence = (
            self.inspect_current_evidence(
                evidence_package
            )
        )


        # ----------------------------------------------------
        # STEP 3 — Historical evidence
        # ----------------------------------------------------

        historical_evidence = (
            self.inspect_historical_evidence(
                evidence_package
            )
        )


        # ----------------------------------------------------
        # STEP 4 — RAG evidence
        # ----------------------------------------------------

        rag_evidence = (
            self.retrieve_domain_knowledge(
                evidence_package
            )
        )


        # ----------------------------------------------------
        # STEP 5 — Evidence assessment
        # ----------------------------------------------------

        assessment = (
            self.assess_evidence(
                evidence_package
            )
        )


        # ----------------------------------------------------
        # STEP 6 — Evidence sufficiency
        # ----------------------------------------------------

        enough_evidence = (
            self.check_evidence_sufficiency(
                evidence_package,
                assessment
            )
        )


        # ----------------------------------------------------
        # STEP 7 — Investigation status
        # ----------------------------------------------------

        if enough_evidence:

            status = "READY_FOR_REASONING"

        else:

            status = "INSUFFICIENT_EVIDENCE"


        # ----------------------------------------------------
        # FINAL INVESTIGATION REPORT
        # ----------------------------------------------------

        report = {

            "incident": evidence_package[
                "incident"
            ],

            "investigation_status": status,

            "building_id": self.building_id,

            "tools_used": self.tools_used,

            "investigation_log": (
                self.investigation_log
            ),

            "current_meter_evidence": (
                current_evidence
            ),

            "historical_evidence": (
                historical_evidence
            ),

            "rag_evidence": (
                rag_evidence
            ),

            "evidence_assessment": (
                assessment
            ),

            "next_stage": (
                "IBM Granite reasoning"
                if enough_evidence
                else
                "Collect additional evidence"
            )
        }


        return report


# ============================================================
# SAVE JSON-SAFE VERSION
# ============================================================

def make_json_safe(obj):

    # Pandas DataFrame
    if isinstance(obj, pd.DataFrame):

        return make_json_safe(
            obj.to_dict(orient="records")
        )

    # Pandas Timestamp
    if isinstance(obj, pd.Timestamp):

        return obj.isoformat()

    # Pandas / NumPy scalar values
    if hasattr(obj, "item"):

        try:
            return obj.item()
        except (ValueError, TypeError):
            pass

    # Dictionary
    if isinstance(obj, dict):

        return {
            str(key): make_json_safe(value)
            for key, value in obj.items()
        }

    # List
    if isinstance(obj, list):

        return [
            make_json_safe(item)
            for item in obj
        ]

    # Tuple
    if isinstance(obj, tuple):

        return [
            make_json_safe(item)
            for item in obj
        ]

    return obj

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== SUSTAINOPS INVESTIGATION AGENT ==========\n"
    )


    # --------------------------------------------------------
    # Incident
    # --------------------------------------------------------

    incident_id = "INC-016"

    incident_start = (
        "2017-10-04 20:00:00"
    )

    incident_end = (
        "2017-10-05 12:00:00"
    )


    # --------------------------------------------------------
    # Create agent
    # --------------------------------------------------------

    agent = InvestigationAgent(
        BUILDING_ID
    )


    # --------------------------------------------------------
    # Run investigation
    # --------------------------------------------------------

    report = agent.generate_report(
        incident_start,
        incident_end,
        incident_id
    )


    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print("Incident:")

    print(
        report["incident"]
    )


    print(
        "\nInvestigation status:"
    )

    print(
        report["investigation_status"]
    )


    print(
        "\nTools used:"
    )

    for tool in report["tools_used"]:

        print(
            f"- {tool}"
        )


    print(
        "\nInvestigation log:"
    )

    for log in report[
        "investigation_log"
    ]:

        print(
            f"- {log}"
        )


    print(
        "\nNext stage:"
    )

    print(
        report["next_stage"]
    )


    # ========================================================
    # SAVE REPORT
    # ========================================================

    OUTPUT_DIR = (
        PROJECT_ROOT / "outputs"
    )

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )


    output_path = (
        OUTPUT_DIR
        / f"{incident_id}_investigation.json"
    )


    json_safe_report = make_json_safe(
        report
    )


    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            json_safe_report,
            file,
            indent=4,
            ensure_ascii=False
        )


    print(
        "\nInvestigation report saved to:"
    )

    print(
        output_path
    )


    print(
        "\n=====================================================\n"
    )