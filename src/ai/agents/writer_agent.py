import asyncio

from agent_framework import Agent

from src.ai.agents.foundry_client import get_client
from src.ai.agents.loader import load_instructions
from src.ai.tools.report_tools import create_chart


def create_writer_agent() -> Agent:
    return Agent(
        client=get_client(),
        name="ReportWriter",
        description="Writes a report or short answer from the Analyst's findings, and can draw a chart from a result_id.",
        instructions=load_instructions("writer"),
        tools=[create_chart],
    )


async def write_report(user_request: str, analyst_findings: str) -> str:
    agent = create_writer_agent()
    prompt = (
        f"User request:\n{user_request}\n\n"
        f"Analyst findings:\n{analyst_findings}"
    )
    result = await agent.run(prompt)
    return str(result)


async def main():
    user_request = "Bar chart of KELA companies created per month this year."
    analyst_findings = (
        "Tool: analyze_companies, filters: supportType = KELA, group_by: month, "
        "date range: 2026-01-01 to 2026-09-25, deleted excluded, "
        "result_id: analyze_companies-9749359c, total: 10, "
        "rows: Jan 0, Feb 0, Mar 1, Apr 2, May 0, Jun 7, Jul 0, Aug 0, Sep 0."
    )
    print(await write_report(user_request, analyst_findings))


if __name__ == "__main__":
    asyncio.run(main())