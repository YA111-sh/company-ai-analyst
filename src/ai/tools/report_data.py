import json
from datetime import date

from src.ai.tools.analytics_tools import (
    get_total_count,
    count_by_column,
    time_series,
    compare_periods,
)


def collect_report_data() -> dict:
    today = date.today()
    year = today.year
    return {
        "generated_on": today.isoformat(),
        "totals": {
            "companies_not_deleted": get_total_count(),
            "companies_all_rows": get_total_count(include_deleted=True),
        },
        "by_support_type": count_by_column("supportType", 10),
        "by_active_status": count_by_column("isActive"),
        "created_per_year": time_series(granularity="year"),
        "created_per_month_this_year": time_series(
            granularity="month", from_date=f"{year}-01-01", to_date=today.isoformat()
        ),
        "year_comparison": compare_periods(
            f"{year - 1}-01-01", f"{year - 1}-12-31",
            f"{year}-01-01", today.isoformat(),
        ),
        "notes": [
            "Deleted companies are excluded unless stated otherwise.",
            "year_comparison: period A is the full previous year, period B is the current year up to today (partial).",
            "A month missing from created_per_month_this_year means zero companies were created in it.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(collect_report_data(), indent=2, default=str))