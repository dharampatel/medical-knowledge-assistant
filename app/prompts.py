from langchain_core.prompts import ChatPromptTemplate

classify_prompt = ChatPromptTemplate.from_template("""
You are an expert domain classifier.
Question: {query}

Answer ONLY with "medical" if this is related to diseases, treatments, drugs, or healthcare. 
Otherwise, answer "other".
""")



refine_prompt = ChatPromptTemplate.from_template("""
You are an expert as query refiner.
The user asked: {query}
But PubMed did not return results.

Suggest a refined query that may retrieve better PubMed results.
Return only the new query.
""")


summarize_prompt = ChatPromptTemplate.from_template("""
You are a medical research assistant. Summarize the following PubMed abstracts 
in bullet points focusing on:
- Treatments, drugs, or interventions
- Outcomes and trial phases
- Publication year

Abstracts: {docs}
""")


explanation_prompt = ChatPromptTemplate.from_template("""
You are an evidence-based clinical explainer. Based on the summary:

{summary}

Write a clear, concise explanation for a clinician, including:
- ✅ Key Findings
- 📊 Evidence Strength
- 📅 Latest Trials
- 🔗 References (cite PubMed IDs if available)

Always end with: 
"⚠️ Disclaimer: This summary is for informational purposes only and not a substitute for medical advice."
""")

