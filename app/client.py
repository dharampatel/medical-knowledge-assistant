import streamlit as st
import requests
import json
import time

st.set_page_config(
    page_title="Medical Assistant",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Medical Assistant")

query = st.text_input("Enter your medical query in Details:")

if st.button("Submit") and query:
    url = f"http://127.0.0.1:8000/ask?query={query}"
    response = requests.get(url, stream=True)

    # Layout split
    left_col, right_col = st.columns([2, 3])

    # Progress bar
    progress_bar = st.progress(0)
    step_counter = 0
    total_steps = 10
    workflow_steps = []
    step_data_store = []

    # Containers
    with left_col:
        stream_container = st.container()
    with right_col:
        final_summary_box = st.container()
        final_explanation_box = st.container()
        final_trials_box = st.container()

    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue

        data_json = line.replace("data: ", "")
        try:
            payload = json.loads(data_json)
        except:
            continue

        node = payload.get("node")
        if not node:  # 🚫 Skip empty or unknown nodes
            continue

        docs_count = payload.get("docs_count", 0)
        summary = payload.get("summary", "")
        explanation = payload.get("explanation", "")
        trials_count = payload.get("trials_count", 0)
        trials = payload.get("trials", [])
        domain = payload.get("domain", "")

        step_data = {
            "node": node,
            "domain": domain,
            "docs_count": docs_count,
            "summary": summary,
            "explanation": explanation,
            "trials_count": trials_count,
            "trials": trials
        }
        step_data_store.append(step_data)
        if node not in workflow_steps:
            workflow_steps.append(node)

        # --- Left panel: Live steps ---
        with stream_container.expander(f"🔹 {node.upper()}", expanded=True):
            st.markdown(f"**Step:** {node}")
            if domain:
                st.markdown(f"**Domain:** {domain}")
            if docs_count:
                st.markdown(f"📄 Retrieved **{docs_count} document(s)**")
            if summary:
                st.markdown(f"📝 Partial Summary:\n{summary[:200]}...")
            if explanation:
                st.markdown(f"💡 Explanation in progress...")
            if trials_count and trials:
                st.markdown(f"**🔬 Clinical Trials ({trials_count}) found...**")

        # --- Right panel: Final outputs ---
        if summary:
            with final_summary_box:
                st.subheader("📝 Medical Final Summary")
                st.markdown(summary)

        if explanation:
            with final_explanation_box:
                st.subheader("💡 Medical Final Explanation")
                st.markdown(explanation)

        if trials_count and trials:
            with final_trials_box:
                st.subheader(f"🔬 Clinical Trials ({trials_count})")
                for trial in trials:
                    st.markdown(
                        f"- **{trial.get('title', 'N/A')}** | "
                        f"Phase: {trial.get('phase', 'N/A')} | "
                        f"Status: {trial.get('status', 'N/A')}"
                    )

        # Update progress live
        step_counter += 1
        progress_bar.progress(min(step_counter / total_steps, 1.0))
        time.sleep(0.09)

    progress_bar.progress(1.0)
    st.success("✅ Workflow Completed!")
