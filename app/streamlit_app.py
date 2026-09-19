
import json
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

st.set_page_config(
    page_title="SustainOps AI",
    page_icon="🌱",
    layout="wide"
)


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        return {"error": str(exc)}


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


st.title("🌱 SustainOps AI")
st.subheader("Evidence-Driven Energy Investigation & Decision Support")

st.caption(
    "Detect unusual energy consumption, investigate possible "
    "explanations, and support human-reviewed sustainability decisions."
)

st.info(
    "Prototype notice: Recommendations are decision-support "
    "suggestions, not confirmed causes or guaranteed savings."
)

# Discover available project outputs
json_files = sorted(OUTPUTS.glob("*.json"))

if not json_files:
    st.warning(
        "No JSON outputs found. Run your investigation, "
        "recommendation, and impact modules first."
    )
    st.stop()

# Incident selector based on available output filenames
incident_ids = sorted({
    path.name.split("_")[0] + "_" + path.name.split("_")[1]
    for path in json_files
    if path.name.startswith("INC-")
    and len(path.name.split("_")) >= 2
})

if not incident_ids:
    incident_ids = ["INC-016"]

incident_id = st.sidebar.selectbox(
    "Select Incident",
    incident_ids
)

st.sidebar.markdown("---")
st.sidebar.caption("SustainOps AI | Prototype")
st.sidebar.caption("Primary SDG: 7 — Affordable and Clean Energy")

# Load incident-related files
incident_files = [
    path for path in json_files
    if path.name.startswith(incident_id)
]

st.header(f"Incident Overview: {incident_id}")

# Display each artifact in an expandable section
for path in incident_files:
    data = load_json(path)

    with st.expander(path.name, expanded=True):
        st.json(data)


# Human review section
st.header("🧑‍💼 Human Review & Audit Trail")

review_path = OUTPUTS / f"{incident_id}_review.json"

if review_path.exists():
    review = load_json(review_path)
    if "error" in review:
        st.error(f"Could not load review file: {review['error']}")
        st.stop()
else:
    review = {
        "incident_id": incident_id,
        "review_status": "PENDING_HUMAN_REVIEW",
        "reviewer_decision": None,
        "reviewer_name": None,
        "reviewer_notes": None,
        "automated_action_taken": False,
        "audit_events": []
    }

st.write("Current review status:", review.get("review_status"))

with st.form(key=f"review_form_{incident_id}", clear_on_submit=False):
    reviewer = st.text_input("Reviewer name (optional)")

    decision = st.selectbox(
        "Review decision",
        [
            "Pending",
            "Accept for further investigation",
            "Reject recommendation",
            "Need more evidence"
        ],
        index=0
    )

    notes = st.text_area(
        "Review notes",
        placeholder="Record verification, concerns, or next steps..."
    )

    submitted = st.form_submit_button(
        "Save Human Review",
        type="primary",
        use_container_width=True
    )

if submitted:
    st.write("Processing review submission...")

    timestamp = datetime.now(timezone.utc).isoformat()

    updated_review = review.copy()
    updated_review["incident_id"] = incident_id
    updated_review["reviewer_name"] = reviewer.strip()
    updated_review["reviewer_decision"] = decision
    updated_review["reviewer_notes"] = notes.strip()
    updated_review["review_status"] = (
        "PENDING_HUMAN_REVIEW"
        if decision == "Pending"
        else "REVIEWED"
    )
    updated_review["automated_action_taken"] = False

    updated_review.setdefault("audit_events", []).append({
        "event": "HUMAN_REVIEW_RECORDED",
        "timestamp_utc": timestamp,
        "reviewer": reviewer.strip(),
        "decision": decision,
        "notes": notes.strip()
    })

    try:
        save_json(review_path, updated_review)

        # Verify that the saved file can be read back
        with review_path.open("r", encoding="utf-8") as f:
            saved_review = json.load(f)

        if saved_review.get("reviewer_decision") != decision:
            st.error("Review verification failed. Saved decision does not match.")
        else:
            st.success("Human review saved and verified successfully!")
            st.json(saved_review)

    except Exception as exc:
        st.error(f"Failed to save human review: {exc}")

st.caption(
    "No equipment is controlled automatically. "
    "Review decisions are recorded for traceability."
)