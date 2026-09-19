from pathlib import Path
import sys
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))


# ============================================================
# IMPORTS
# ============================================================

from evidence import build_evidence_package


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BUILDING_ID = "Eagle_education_Wesley"


# ============================================================
# HELPER: GET RAG TEXT
# ============================================================

def get_rag_text(rag_evidence):
    """
    Combine retrieved RAG evidence into one searchable text block.
    """

    texts = []

    for item in rag_evidence:

        for result in item["results"]:

            text = result.get("text", "")

            if text:
                texts.append(text.lower())

    return "\n".join(texts)


# ============================================================
# ANALYZE HISTORICAL EVIDENCE
# ============================================================

def analyze_historical_evidence(historical_evidence):
    """
    Analyze the historical electricity comparison.

    The function identifies:

    - positive deviations
    - negative deviations
    - strongest positive deviation
    - strongest negative deviation
    - amount of historical support
    """

    if historical_evidence.empty:

        return {
            "status": "NO_EVIDENCE",
            "positive_count": 0,
            "negative_count": 0,
            "strongest_positive_deviation": None,
            "strongest_negative_deviation": None,
            "average_positive_deviation": None,
            "average_negative_deviation": None,
            "average_history_count": 0
        }


    data = historical_evidence.copy()

    valid = data[
        data["relative_deviation"].notna()
    ].copy()


    if valid.empty:

        return {
            "status": "NO_VALID_EVIDENCE",
            "positive_count": 0,
            "negative_count": 0,
            "strongest_positive_deviation": None,
            "strongest_negative_deviation": None,
            "average_positive_deviation": None,
            "average_negative_deviation": None,
            "average_history_count": 0
        }


    positive = valid[
        valid["relative_deviation"] > 0
    ]

    negative = valid[
        valid["relative_deviation"] < 0
    ]


    strongest_positive = None

    if not positive.empty:

        strongest_positive = positive.loc[
            positive["relative_deviation"].idxmax()
        ]


    strongest_negative = None

    if not negative.empty:

        strongest_negative = negative.loc[
            negative["relative_deviation"].idxmin()
        ]


    average_positive = None

    if not positive.empty:

        average_positive = positive[
            "relative_deviation"
        ].mean()


    average_negative = None

    if not negative.empty:

        average_negative = negative[
            "relative_deviation"
        ].mean()


    return {
        "status": "AVAILABLE",

        "positive_count": len(positive),

        "negative_count": len(negative),

        "strongest_positive_deviation": (
            float(
                strongest_positive[
                    "relative_deviation"
                ]
            )
            if strongest_positive is not None
            else None
        ),

        "strongest_negative_deviation": (
            float(
                strongest_negative[
                    "relative_deviation"
                ]
            )
            if strongest_negative is not None
            else None
        ),

        "average_positive_deviation": (
            float(average_positive)
            if average_positive is not None
            else None
        ),

        "average_negative_deviation": (
            float(average_negative)
            if average_negative is not None
            else None
        ),

        "average_history_count": float(
            valid["history_count"].mean()
        )
    }


# ============================================================
# BUILD HYPOTHESIS ASSESSMENT
# ============================================================

def build_hypothesis_assessment(
    hypothesis,
    supporting_evidence,
    contradicting_evidence,
    evidence_quality
):
    """
    Create a transparent assessment for one hypothesis.

    No causal probability is assigned.
    """

    return {
        "hypothesis": hypothesis,
        "supporting_evidence": supporting_evidence,
        "contradicting_evidence": contradicting_evidence,
        "evidence_quality": evidence_quality
    }


# ============================================================
# SCORE EVIDENCE
# ============================================================

def score_evidence(evidence_package):
    """
    Convert the evidence package into structured
    evidence assessments.

    IMPORTANT:
    This is evidence assessment, NOT causal probability.
    """

    historical_evidence = (
        evidence_package["historical_evidence"]
    )

    rag_evidence = (
        evidence_package["rag_evidence"]
    )


    # --------------------------------------------------------
    # Analyze historical pattern
    # --------------------------------------------------------

    historical_summary = analyze_historical_evidence(
        historical_evidence
    )


    # --------------------------------------------------------
    # RAG text
    # --------------------------------------------------------

    rag_text = get_rag_text(
        rag_evidence
    )


    # ========================================================
    # HYPOTHESIS 1 — OPERATING SCHEDULE
    # ========================================================

    operational_support = []

    operational_contradictions = []


    if "operating schedule" in rag_text:

        operational_support.append(
            "Retrieved domain knowledge identifies "
            "unusual operating schedules as a possible "
            "explanation for energy anomalies."
        )


    if "occupancy" in rag_text:

        operational_support.append(
            "Retrieved domain knowledge identifies "
            "changes in occupancy as a possible factor."
        )


    if (
        historical_summary["status"] == "AVAILABLE"
        and historical_summary["positive_count"] > 0
    ):

        operational_support.append(
            "Historical evidence shows periods where "
            "electricity consumption exceeded the "
            "historical reference."
        )


    if (
        historical_summary["negative_count"] > 0
    ):

        operational_contradictions.append(
            "The incident also contains substantial "
            "periods below the historical reference, "
            "so the entire incident cannot be described "
            "as uniformly high consumption."
        )


    operational_assessment = build_hypothesis_assessment(
        "Possible unusual building operating schedule",
        operational_support,
        operational_contradictions,
        "MODERATE"
    )


    # ========================================================
    # HYPOTHESIS 2 — HVAC
    # ========================================================

    hvac_support = []

    hvac_contradictions = []


    if "hvac" in rag_text:

        hvac_support.append(
            "Retrieved domain knowledge indicates that "
            "heating or cooling-related behavior can "
            "coincide with unusual electricity consumption."
        )


    if "heating or cooling" in rag_text:

        hvac_support.append(
            "The knowledge base recommends examining "
            "heating/cooling-related meter behavior "
            "during electricity anomaly investigation."
        )


    if (
        historical_summary["positive_count"] > 0
    ):

        hvac_support.append(
            "Historical evidence confirms that electricity "
            "was above its historical reference during "
            "several incident observations."
        )


    hvac_contradictions.append(
        "Current supporting-meter values alone do not "
        "establish that HVAC behavior caused the "
        "electricity deviation."
    )


    hvac_contradictions.append(
        "Additional historical behavior of the HVAC-related "
        "supporting meter would be required for stronger "
        "evidence."
    )


    hvac_assessment = build_hypothesis_assessment(
        "Possible HVAC-related behavior",
        hvac_support,
        hvac_contradictions,
        "MODERATE"
    )


    # ========================================================
    # HYPOTHESIS 3 — LIGHTING / EQUIPMENT
    # ========================================================

    equipment_support = []

    equipment_contradictions = []


    if "lighting" in rag_text:

        equipment_support.append(
            "Retrieved domain knowledge identifies "
            "lighting as a contributor to building "
            "electricity consumption."
        )


    if "equipment" in rag_text:

        equipment_support.append(
            "Retrieved domain knowledge identifies "
            "equipment operation and operating schedules "
            "as possible contributors to unusual "
            "electricity consumption."
        )


    if (
        historical_summary["positive_count"] > 0
    ):

        equipment_support.append(
            "Historical evidence shows several periods "
            "above the historical electricity reference."
        )


    equipment_contradictions.append(
        "Electricity meter data alone cannot identify "
        "which individual equipment or lighting system "
        "was responsible."
    )


    equipment_contradictions.append(
        "Operational or equipment records are needed "
        "to strengthen this hypothesis."
    )


    equipment_assessment = build_hypothesis_assessment(
        "Possible lighting or equipment operation",
        equipment_support,
        equipment_contradictions,
        "MODERATE"
    )


    # ========================================================
    # OVERALL EVIDENCE QUALITY
    # ========================================================

    evidence_quality = {

        "historical_evidence": (
            historical_summary["status"]
        ),

        "historical_observations": (
            len(historical_evidence)
        ),

        "average_history_count": (
            historical_summary[
                "average_history_count"
            ]
        ),

        "rag_sources": len(rag_evidence),

        "limitations": [
            "Historical comparisons use a limited "
            "number of previous observations.",

            "Supporting meter magnitudes are not directly "
            "comparable because they use different scales.",

            "RAG evidence provides domain knowledge and "
            "investigation guidance, not proof of a specific "
            "cause.",

            "No causal conclusion should be made without "
            "additional operational evidence."
        ]
    }


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "incident": evidence_package["incident"],

        "historical_summary": historical_summary,

        "hypotheses": [

            operational_assessment,

            hvac_assessment,

            equipment_assessment

        ],

        "evidence_quality": evidence_quality
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== SUSTAINOPS EVIDENCE SCORING ==========\n"
    )


    # --------------------------------------------------------
    # Select incident
    # --------------------------------------------------------

    incident_start = "2017-10-04 20:00:00"

    incident_end = "2017-10-05 12:00:00"


    # --------------------------------------------------------
    # Build evidence package
    # --------------------------------------------------------

    package = build_evidence_package(
        incident_start,
        incident_end,
        incident_id="INC-016"
    )


    # --------------------------------------------------------
    # Score / assess evidence
    # --------------------------------------------------------

    assessment = score_evidence(
        package
    )


    # ========================================================
    # INCIDENT
    # ========================================================

    print("Incident:")

    print(
        assessment["incident"]
    )


    # ========================================================
    # HISTORICAL SUMMARY
    # ========================================================

    print("\n--- Historical Summary ---")

    print(
        assessment["historical_summary"]
    )


    # ========================================================
    # HYPOTHESES
    # ========================================================

    print("\n--- Hypothesis Assessments ---")


    for index, hypothesis in enumerate(
        assessment["hypotheses"],
        start=1
    ):

        print(
            f"\nHypothesis {index}:"
        )

        print(
            hypothesis["hypothesis"]
        )

        print(
            "\nEvidence quality:"
        )

        print(
            hypothesis["evidence_quality"]
        )

        print(
            "\nSupporting evidence:"
        )

        for item in hypothesis[
            "supporting_evidence"
        ]:

            print(
                f"- {item}"
            )

        print(
            "\nContradicting / limiting evidence:"
        )

        for item in hypothesis[
            "contradicting_evidence"
        ]:

            print(
                f"- {item}"
            )


    # ========================================================
    # OVERALL EVIDENCE QUALITY
    # ========================================================

    print(
        "\n--- Overall Evidence Quality ---"
    )

    print(
        assessment["evidence_quality"]
    )


    # ========================================================
    # END
    # ========================================================

    print(
        "\n==================================================\n"
    )