from datetime import date, timedelta

from agent_framework import tool

from src.ai.db.queries import TABLE, fetch_rows, fetch_scalar
from src.ai.run_context import get_context

ALLOWED_GROUP_COLUMNS = {
    "isActive", "deleted", "supportType", "tvvID", "financialLoadType",
    "allowProductsForPerson", "createdBy", "updatedBy",
    "workMunicipality", "addressMunicipality",
}

SUPPORT_TYPE_LABELS = {
    1: "TSL", 2: "HLO", 3: "KOULU", 4: "LASK", 5: "VPL",
    6: "KELA", 7: "AKTIIVI", 8: "OPIS", 9: "MAKOS",
}
SUPPORT_TYPE_CODES = {label: code for code, label in SUPPORT_TYPE_LABELS.items()}

ALLOWED_DATE_COLUMNS = {"createdDateTime", "startDate", "deleteDate", "updatedDateTime"}

_PERIOD_SQL = {
    "day": "CAST([{c}] AS date)",
    "month": "DATEFROMPARTS(YEAR([{c}]), MONTH([{c}]), 1)",
    "year": "DATEFROMPARTS(YEAR([{c}]), 1, 1)",
}

FILTERABLE_COLUMNS = ALLOWED_GROUP_COLUMNS


@tool(approval_mode="never_require")
def compare_periods(
    period_a_from: str,
    period_a_to: str,
    period_b_from: str,
    period_b_to: str,
    date_column: str = "createdDateTime",
    include_deleted: bool = False,
) -> dict:
    """Compare company counts in two date ranges (YYYY-MM-DD, inclusive). Period A is the baseline, period B is compared to it."""
    if date_column not in ALLOWED_DATE_COLUMNS:
        return {"error": f"date_column must be one of {sorted(ALLOWED_DATE_COLUMNS)}"}
    try:
        a_start = date.fromisoformat(period_a_from)
        a_end = date.fromisoformat(period_a_to)
        b_start = date.fromisoformat(period_b_from)
        b_end = date.fromisoformat(period_b_to)
    except ValueError:
        return {"error": "Dates must be in YYYY-MM-DD format"}

    where = f"[{date_column}] IS NOT NULL"
    if date_column != "deleteDate" and not include_deleted:
        where += " AND deleted = 0"

    sql = f"""
        SELECT
            COALESCE(SUM(CASE WHEN [{date_column}] >= :a_start AND [{date_column}] < :a_end THEN 1 ELSE 0 END), 0) AS count_a,
            COALESCE(SUM(CASE WHEN [{date_column}] >= :b_start AND [{date_column}] < :b_end THEN 1 ELSE 0 END), 0) AS count_b
        FROM {TABLE}
        WHERE {where}
    """
    params = {
        "a_start": a_start, "a_end": a_end + timedelta(days=1),
        "b_start": b_start, "b_end": b_end + timedelta(days=1),
    }
    row = fetch_rows(sql, params)[0]
    count_a, count_b = int(row["count_a"]), int(row["count_b"])
    percent_change = round((count_b - count_a) * 100.0 / count_a, 1) if count_a else None

    return {
        "date_column": date_column,
        "period_a": {"from": period_a_from, "to": period_a_to, "count": count_a},
        "period_b": {"from": period_b_from, "to": period_b_to, "count": count_b},
        "change": count_b - count_a,
        "percent_change": percent_change,
    }


def _fill_missing_periods(rows: list[dict], granularity: str, start: date | None, end: date | None) -> list[dict]:
    """Add rows with count 0 for months or years that have no companies."""
    if not rows and not (start and end):
        return rows
    first = start or date.fromisoformat(rows[0]["value"])
    last = end or date.fromisoformat(rows[-1]["value"])
    counts = {r["value"]: r["count"] for r in rows}

    by_month = granularity == "month"
    year, month = first.year, (first.month if by_month else 1)
    end_key = (last.year, last.month if by_month else 1)

    filled = []
    while (year, month) <= end_key:
        key = date(year, month, 1).isoformat()
        filled.append({"value": key, "count": counts.get(key, 0)})
        if by_month:
            month += 1
            if month == 13:
                year, month = year + 1, 1
        else:
            year += 1
    return filled


@tool(approval_mode="never_require")
def analyze_companies(
    group_by: str | None = None,
    support_type: str | None = None,
    is_active: bool | None = None,
    created_by: str | None = None,
    updated_by: str | None = None,
    work_municipality: str | None = None,
    address_municipality: str | None = None,
    date_column: str = "createdDateTime",
    from_date: str | None = None,
    to_date: str | None = None,
    include_deleted: bool = False,
    top_n: int = 20,
) -> dict:
    """Flexible company count. Optional filters, optional grouping, optional date range.
    group_by: one of isActive, deleted, supportType, tvvID, financialLoadType, allowProductsForPerson,
      createdBy, updatedBy, workMunicipality, addressMunicipality, or 'year' / 'month'
      (which groups by date_column). Leave empty for a single total.
    support_type: filter by support type label, for example 'KELA' or 'TSL'.
    is_active: filter by active status (true/false).
    created_by / updated_by / work_municipality / address_municipality: filter by these columns' exact value.
    date_column: createdDateTime, startDate, deleteDate or updatedDateTime. Dates are YYYY-MM-DD.
    Deleted companies are excluded unless include_deleted is true."""

    filters: dict[str, object] = {}
    if support_type is not None:
        filters["supportType"] = support_type
    if is_active is not None:
        filters["isActive"] = is_active
    if created_by is not None:
        filters["createdBy"] = created_by
    if updated_by is not None:
        filters["updatedBy"] = updated_by
    if work_municipality is not None:
        filters["workMunicipality"] = work_municipality
    if address_municipality is not None:
        filters["addressMunicipality"] = address_municipality
    if date_column not in ALLOWED_DATE_COLUMNS:
        return {"error": f"date_column must be one of {sorted(ALLOWED_DATE_COLUMNS)}"}
    if group_by is not None and group_by not in ALLOWED_GROUP_COLUMNS and group_by not in _PERIOD_SQL:
        return {"error": f"group_by must be one of {sorted(ALLOWED_GROUP_COLUMNS | {'year', 'month'})}"}
    try:
        start = date.fromisoformat(from_date) if from_date else None
        end = date.fromisoformat(to_date) if to_date else None
    except ValueError:
        return {"error": "Dates must be in YYYY-MM-DD format"}

    conditions: list[str] = []
    params: dict = {}

    if group_by == "deleted":
        include_deleted = True
    if not include_deleted and date_column != "deleteDate":
        conditions.append("deleted = 0")

    for i, (col, val) in enumerate(filters.items()):
        if col not in FILTERABLE_COLUMNS:
            return {"error": f"Cannot filter on '{col}'. Allowed: {sorted(FILTERABLE_COLUMNS)}"}
        if col == "supportType" and isinstance(val, str):
            code = SUPPORT_TYPE_CODES.get(val.upper())
            if code is None:
                return {"error": f"Unknown supportType '{val}'. Allowed: {sorted(SUPPORT_TYPE_CODES)}"}
            val = code
        if val is None:
            conditions.append(f"[{col}] IS NULL")
        else:
            conditions.append(f"[{col}] = :f{i}")
            params[f"f{i}"] = val

    if start or end or group_by in _PERIOD_SQL:
        conditions.append(f"[{date_column}] IS NOT NULL")
    if start:
        conditions.append(f"[{date_column}] >= :start")
        params["start"] = start
    if end:
        conditions.append(f"[{date_column}] < :end_exclusive")
        params["end_exclusive"] = end + timedelta(days=1)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    total = fetch_scalar(f"SELECT COUNT(*) FROM {TABLE} {where}", params)

    if group_by is None:
        rows = [{"value": "all", "count": total}]
    elif group_by in _PERIOD_SQL:
        expr = _PERIOD_SQL[group_by].format(c=date_column)
        rows = fetch_rows(
            f"SELECT {expr} AS value, COUNT(*) AS count FROM {TABLE} {where} "
            f"GROUP BY {expr} ORDER BY {expr}",
            params,
        )
        for row in rows:
            row["value"] = row["value"].isoformat()
        rows = _fill_missing_periods(rows, group_by, start, end)
    else:
        rows = fetch_rows(
            f"SELECT TOP (:n) [{group_by}] AS value, COUNT(*) AS count FROM {TABLE} {where} "
            f"GROUP BY [{group_by}] ORDER BY COUNT(*) DESC",
            {**params, "n": max(1, min(top_n, 50))},
        )
        if group_by == "supportType":
            for row in rows:
                row["label"] = SUPPORT_TYPE_LABELS.get(row["value"], "UNKNOWN")

    result = {
        "group_by": group_by, "filters": filters, "date_column": date_column,
        "from_date": from_date, "to_date": to_date, "include_deleted": include_deleted,
        "total": total, "rows": rows,
    }
    arguments = {
        "group_by": group_by, "filters": filters, "date_column": date_column,
        "from_date": from_date, "to_date": to_date,
        "include_deleted": include_deleted, "top_n": top_n,
    }
    result_id = get_context().record("analyze_companies", arguments, result, 0)
    return {**result, "result_id": result_id}