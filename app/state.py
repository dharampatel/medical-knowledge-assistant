from typing import TypedDict, List, Optional
from langchain_core.documents import Document

class AgentState(TypedDict):
    query: str
    docs: List[Document]
    summary: str
    explanation: str
    domain: Optional[str]
    refine_count: int
    trials: Optional[List[dict]]
