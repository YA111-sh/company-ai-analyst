from pathlib import Path

import matplotlib

matplotlib.use("Agg")   # draw to files only, no window (needed on servers)
import matplotlib.pyplot as plt

from src.ai.run_context import get_context

CHART_DIR = Path(__file__).resolve().parents[1] / "reports" / "output" / "charts"


def _label(row: dict, group_by: str | None) -> str:
    if row.get("label"):
        return str(row["label"])
    value = row["value"]
    if value is None:
        return "(empty)"
    if group_by == "month":
        return str(value)[:7]
    if group_by == "year":
        return str(value)[:4]
    return str(value)


def create_chart(result_id: str, chart_type: str = "bar", title: str = "") -> dict:
    """Draw a chart image (PNG) from a stored analyze_companies result.
    result_id: the result_id returned by analyze_companies.
    chart_type: 'bar' for categories such as support types, 'line' for trends over time.
    title: a short descriptive title. Returns the image file path."""
    if chart_type not in ("bar", "line"):
        return {"error": "chart_type must be 'bar' or 'line'"}

    call = get_context().get(result_id)
    if call is None or not isinstance(call.result, dict) or "rows" not in call.result:
        return {"error": f"Unknown result_id '{result_id}'. Use the result_id returned by analyze_companies."}

    result = call.result
    rows = result["rows"]
    if not rows:
        return {"error": "The stored result has no rows to chart."}

    group_by = result.get("group_by")
    labels = [_label(r, group_by) for r in rows]
    counts = [r["count"] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5))
    if chart_type == "bar":
        bars = ax.bar(labels, counts, color="#2f6fdd")
        ax.bar_label(bars)
    else:
        ax.plot(labels, counts, marker="o", color="#2f6fdd")
        for x, y in zip(labels, counts):
            ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 6), ha="center")

    ax.set_title(title or "Companies")
    ax.set_ylabel("Companies")
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    path = CHART_DIR / f"{result_id}-{chart_type}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)

    return {"file_path": str(path), "chart_type": chart_type, "points": len(rows)}


if __name__ == "__main__":
    from src.ai.tools.analytics_tools import analyze_companies

    r = analyze_companies(group_by="supportType")
    print(create_chart(r["result_id"], "bar", "Companies per support type"))

    r = analyze_companies(group_by="month", from_date="2026-01-01", to_date="2026-12-31")
    print(create_chart(r["result_id"], "line", "Companies created per month, 2026"))