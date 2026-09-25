import asyncio
import json

from src.ai.agents.workflows import run_report


async def main():
    for request in [
        "How many KELA companies are there in total?",
        "Bar chart of companies per support type.",
        "How many active companies were created last year?",
    ]:
        print("\n" + "=" * 60)
        print("REQUEST:", request)
        result = await run_report(request)
        print("REPORT:\n", result["report"])
        print("TOOL CALLS:", json.dumps(result["tool_calls"], indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())