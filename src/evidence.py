from pathlib import Path
import sys


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

from investigation import (
    get_incident_evidence,
    load_building_data,
    prepare_meter_data
)

from historical_evidence import (
    prepare_electricity_data,
    find_historical_comparisons
)

from rag_retriever import retrieve_knowledge


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BUILDING_ID = "Eagle_education_Wesley"


# ============================================================
# BUILD EVIDENCE PACKAGE
# ============================================================

def build_evidence_package(
    incident_start,
    incident_end,
    incident_id="INC-016"
):
    """
    Build a structured evidence package for an energy incident.

    Evidence sources:

    1. Current meter evidence
    2. Historical electricity evidence
    3. RAG/domain knowledge
    """

    # ========================================================
    # 1. LOAD ALL BUILDING DATA
    # ========================================================

    building_data = load_building_data()


    # ========================================================
    # 2. PREPARE METER DATA
    # ========================================================

    # Returns a dictionary containing:
    #
    # electricity
    # steam
    # chilled_water
    # hot_water

    meter_data = prepare_meter_data(
        building_data,
        BUILDING_ID
    )


    # ========================================================
    # 3. CURRENT METER EVIDENCE
    # ========================================================

    current_evidence = get_incident_evidence(
        meter_data,
        incident_start,
        incident_end
    )


    # ========================================================
    # 4. PREPARE ELECTRICITY FOR HISTORICAL ANALYSIS
    # ========================================================

    # IMPORTANT:
    #
    # We use the existing function from
    # historical_evidence.py.
    #
    # This guarantees that the historical analysis receives
    # exactly the structure that find_historical_comparisons()
    # expects.

    electricity = prepare_electricity_data(
        building_data
    )


    # ========================================================
    # 5. CONVERT INCIDENT TIMES TO TIMESTAMPS
    # ========================================================

    incident_start_timestamp = (
        __import__("pandas").Timestamp(incident_start)
    )

    incident_end_timestamp = (
        __import__("pandas").Timestamp(incident_end)
    )


    # ========================================================
    # 6. HISTORICAL EVIDENCE
    # ========================================================

    historical_evidence = find_historical_comparisons(
        electricity,
        incident_start_timestamp,
        incident_end_timestamp
    )


    # ========================================================
    # 7. RAG / DOMAIN KNOWLEDGE EVIDENCE
    # ========================================================

    rag_queries = [

        (
            "Could HVAC-related behavior explain "
            "an unusual electricity anomaly?"
        ),

        (
            "Could unusual building operating schedules "
            "explain an electricity anomaly?"
        ),

        (
            "Could lighting or equipment operation "
            "explain unexpectedly high electricity consumption?"
        )
    ]


    rag_evidence = []


    for query in rag_queries:

        results = retrieve_knowledge(
            query,
            top_k=2
        )

        rag_evidence.append(
            {
                "query": query,
                "results": results
            }
        )


    # ========================================================
    # 8. COMBINE ALL EVIDENCE
    # ========================================================

    evidence_package = {

        "incident": {
            "incident_id": incident_id,
            "building_id": BUILDING_ID,
            "start": str(incident_start),
            "end": str(incident_end)
        },

        "current_meter_evidence": current_evidence,

        "historical_evidence": historical_evidence,

        "rag_evidence": rag_evidence
    }


    # ========================================================
    # 9. RETURN PACKAGE
    # ========================================================

    return evidence_package


# ============================================================
# TEST EVIDENCE PACKAGE
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== SUSTAINOPS EVIDENCE PACKAGE ==========\n"
    )


    # --------------------------------------------------------
    # Incident selected for investigation
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


    # ========================================================
    # INCIDENT
    # ========================================================

    print("Incident:")

    print(package["incident"])


    # ========================================================
    # CURRENT METER EVIDENCE
    # ========================================================

    print("\n--- Current Meter Evidence ---")

    for meter, data in package["current_meter_evidence"].items():

        print(f"\n{meter}:")

        print(data.to_string(index=False))


    # ========================================================
    # HISTORICAL EVIDENCE
    # ========================================================

    print("\n--- Historical Evidence ---")

    if package["historical_evidence"].empty:

        print("No historical comparison records found.")

    else:

        print(
            package["historical_evidence"].to_string(
                index=False
            )
        )


    # ========================================================
    # RAG EVIDENCE
    # ========================================================

    print("\n--- RAG Evidence ---")

    for item in package["rag_evidence"]:

        print("\nQuery:")

        print(item["query"])


        for result in item["results"]:

            print(
                f"\nSource: {result['source']}"
            )

            print(
                f"Chunk: {result['chunk']}"
            )

            print(
                f"Distance: {result['distance']:.4f}"
            )

            print("\nText:")

            print(result["text"])


    # ========================================================
    # END
    # ========================================================

    print(
        "\n==================================================\n"
    )