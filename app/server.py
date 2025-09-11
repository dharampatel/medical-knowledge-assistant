import asyncio

from app.workflow import build_workflow


async def main():
    query = "Latest treatment options for glioblastoma"
    graph = build_workflow()
    result = await graph.ainvoke({"query": query})

    print("\n--- SUMMARY ---\n")
    print(result["summary"])
    print("\n--- FINAL EXPLANATION ---\n")
    print(result["explanation"])



async def stream_main():
    graph = build_workflow()

    query = "Latest treatment options for glioblastoma"

    print("\n--- STREAMING OUTPUT ---\n")

    async for event in graph.astream({"query": query}):
        # `event` is a dictionary with node outputs
        for node, state in event.items():
            print(f"\n🔹 Node reached: {node}")
            if "summary" in state:
                print(f"  Summary:\n{state['summary'][:300]}...")
            if "explanation" in state:
                print(f"  Explanation:\n{state['explanation'][:300]}...")
            if "docs" in state:
                print(f"  Retrieved {len(state['docs'])} docs")

    print("\n✅ Streaming finished.\n")

if __name__ == "__main__":
    asyncio.run(stream_main())
