import asyncio

from agent_framework import Agent
from datetime import date

from src.ai.agents.foundry_client import get_client
from src.ai.agents.loader import load_instructions
from src.ai.tools.analytics_tools import (
    analyze_companies,
    compare_periods,
)


def create_analyst_agent() -> Agent:
    return Agent(
        client=get_client(),
        name="DataAnalyst",
        description="Answers questions about the Company table by filtering, grouping and counting companies, and comparing periods.",
        instructions=load_instructions("analyst") + f"\n\n# Current date\nToday's date is {date.today().isoformat()}.",
        tools=[analyze_companies, compare_periods],
    )


async def main():
    agent = create_analyst_agent()
    questions = ["KELA companies created per month last year?"]
    for q in questions:
        print("\nQ:", q)
        result = await agent.run(q)
        print("A:", result)

    from src.ai.run_context import get_context
    print("\nTool calls:")
    for call in get_context().all():
        print(call.id, call.tool, call.arguments)


if __name__ == "__main__":
    asyncio.run(main())