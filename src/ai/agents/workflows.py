from src.ai.agents.analyst_agent import create_analyst_agent
from src.ai.agents.writer_agent import write_report
from src.ai.run_context import reset_context, get_context


async def run_report(user_request: str) -> dict:
    reset_context()

    analyst = create_analyst_agent()
    findings = await analyst.run(user_request)
    findings_text = str(findings)

    tool_calls = get_context().all()
    if not tool_calls:
        findings_text = (
            "WARNING: no tool was called, so the following text is unverified "
            "and may contain incorrect numbers:\n" + findings_text
        )

    report = await write_report(user_request, findings_text)

    return {
        "user_request": user_request,
        "findings": findings_text,
        "report": report,
        "verified": bool(tool_calls),
        "tool_calls": [
            {"id": c.id, "tool": c.tool, "arguments": c.arguments}
            for c in tool_calls
        ],
    }