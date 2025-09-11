from app.config import retriever, llm
from app.prompts import summarize_prompt, explanation_prompt, classify_prompt, refine_prompt
from app.state import AgentState
from typing import Optional, Callable
import httpx

StatusCallback = Optional[Callable[[str], None]]

def rank_documents(docs):
    """
    Simple heuristic ranking:
    - Recent publications rank higher
    - Clinical trial papers rank higher than reviews
    - Sort by score (e.g., citation count, retriever score)
    """
    ranked = sorted(
        docs,
        key=lambda d: (
            d.metadata.get("is_clinical_trial", False),
            d.metadata.get("year", 0),
            d.metadata.get("score", 0)
        ),
        reverse=True
    )
    return ranked

async def classify_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback: status_callback("🔹 Classifying query domain...")
    messages = classify_prompt.format_messages(query=state["query"])
    result = (await llm.ainvoke(messages)).content.strip().lower()
    state["domain"] = "medical" if "medical" in result else "other"
    return state


async def off_domain_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback: status_callback("❌ Query is off-domain")
    state["explanation"] = (
        "❌ The question is outside the medical domain (off-domain). "
        "This assistant only answers medical and biomedical queries."
    )
    return state

async def no_answer_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback: status_callback("❌ No answer found for the query.")
    state["explanation"] = "❌ The question is outside the medical domain. No answer can be provided."
    return state

async def retrieve_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback: status_callback("🔹 Retrieving documents from PubMed...")
    docs = await retriever.ainvoke(state["query"])
    state["docs"] = rank_documents(docs)
    return state


async def fetch_trials_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback:
        status_callback("🔹 Fetching clinical trials from ClinicalTrials.gov...")

    url = "https://clinicaltrials.gov/api/query/full_studies"
    params = {
        "expr": state["query"],
        "min_rnk": 1,
        "max_rnk": 5,
        "fmt": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        if status_callback:
            status_callback(f"⚠️ Failed to fetch trials: {str(e)}")
        state["trials"] = []
        return state

    trials = []
    for study in data.get("FullStudiesResponse", {}).get("FullStudies", []):
        study_data = study.get("Study", {})
        trials.append({
            "title": study_data.get("ProtocolSection", {}).get("IdentificationModule", {}).get("OfficialTitle", ""),
            "status": study_data.get("ProtocolSection", {}).get("StatusModule", {}).get("OverallStatus", ""),
            "phase": study_data.get("ProtocolSection", {}).get("DesignModule", {}).get("PhaseList", {}).get("Phase", []),
            "start_date": study_data.get("ProtocolSection", {}).get("StatusModule", {}).get("StartDateStruct", {}).get("StartDate", ""),
            "completion_date": study_data.get("ProtocolSection", {}).get("StatusModule", {}).get("CompletionDateStruct", {}).get("CompletionDate", "")
        })

    state["trials"] = trials
    return state


async def refine_query_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback: status_callback("🔹 Refining query to find relevant documents...")
    messages = refine_prompt.format_messages(query=state["query"])
    new_query = (await llm.ainvoke(messages)).content.strip()
    state["query"] = new_query
    return state


async def summarize_node(state: AgentState, status_callback: StatusCallback = None):
    if not state["docs"]:
        if status_callback: status_callback("⚠️ No relevant PubMed abstracts found")
        state["summary"] = "No relevant PubMed abstracts found."
        return state

    if status_callback: status_callback("🔹 Summarizing retrieved documents...")
    docs_text = "\n\n".join([d.page_content for d in state["docs"]])
    messages = summarize_prompt.format_messages(docs=docs_text)
    summary = (await llm.ainvoke(messages)).content
    state["summary"] = summary
    return state


async def explain_node(state: AgentState, status_callback: StatusCallback = None):
    if status_callback: status_callback("🔹 Generating detailed explanation...")
    messages = explanation_prompt.format_messages(summary=state["summary"])
    explanation = (await llm.ainvoke(messages)).content
    state["explanation"] = explanation
    return state


async def retrieve_with_refine_node(state: AgentState, status_callback: StatusCallback = None):
    """
    Retrieve documents, refine query up to 2 times if no documents found,
    then fallback to no_answer_node if still empty.
    """
    max_refines = 2
    attempt = 0

    while attempt <= max_refines:
        await retrieve_node(state, status_callback=status_callback)
        if state["docs"]:
            return state
        if attempt < max_refines:
            await refine_query_node(state, status_callback=status_callback)
        attempt += 1

    # Fallback
    if status_callback: status_callback("❌ No documents found after refinement")
    state["summary"] = "No relevant documents found after query refinement."
    state["explanation"] = "❌ Unable to provide an answer based on the current knowledge."
    return state
