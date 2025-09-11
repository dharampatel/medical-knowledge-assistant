from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

from app.workflow import build_workflow

app = FastAPI(title="Medical Knowledge Assistant API 🚀")

# Build the workflow
graph = build_workflow()

@app.get("/")
async def root():
    return {"message": "Medical Knowledge Assistant API running 🚀"}




@app.get("/ask")
async def ask(query: str):
    async def event_generator():
        async for event in graph.astream({"query": query}):
            for node_name, state in event.items():
                payload = {"node": node_name}
                if "docs" in state:
                    payload["docs_count"] = len(state["docs"])
                if "trials" in state:
                    payload["trials_count"] = len(state["trials"])
                    payload["trials"] = state["trials"]
                if "summary" in state:
                    payload["summary"] = state["summary"]
                if "explanation" in state:
                    payload["explanation"] = state["explanation"]
                if "domain" in state:
                    payload["domain"] = state["domain"]
                if "refine_count" in state:
                    payload["refine_count"] = state["refine_count"]

                yield f"data: {json.dumps(payload)}\n\n"

        # Always send a final "done" event before closing
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
        },
    )
