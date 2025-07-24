# File: app/services/fetch_dashboard_data.py

from sqlalchemy import text
from app.db import engine
from app.services.utils.time_filters import get_date_ranges
from .chart_configs import chart_configs, DRILL_LVL1, DRILL_LVL2

# Human‑friendly labels for dimensions
ALL_DIMS = {
    "credit_card_type":     "Card Type",
    "transaction_currency": "Currency",
    "name":                 "Acquirer",
}

# How to qualify each dimension in SQL
QUALIFIED_FIELDS = {
    "credit_card_type":     "t.credit_card_type",
    "transaction_currency": "t.transaction_currency",
    "name":                 "a.name",
}

def get_dashboard_data(filter_type: str,
                       custom:      tuple = None,
                       drill_keys:  dict  = None) -> dict:
    drill_keys = drill_keys or {}
    start, end, _, _ = get_date_ranges(filter_type, custom)

    where_clause = "WHERE t.created_at BETWEEN :s AND :e"
    base_params  = {"s": start, "e": end}

    # Identify which base chart was clicked (if any)
    base_clicked = next(
        (k for k in drill_keys.keys() if k not in (DRILL_LVL1, DRILL_LVL2)),
        None
    )

    metrics = []
    charts  = []

    with engine.connect() as conn:
        # ─── Metrics (date‑filtered) ─────────────────────────
        total_volume = conn.execute(
            text("SELECT COALESCE(SUM(t.usd_value),0) FROM live_transactions t"),
            base_params
        ).scalar() or 0.0

        avg_value = conn.execute(
            text("SELECT COALESCE(AVG(t.usd_value),0) FROM live_transactions t"),
            base_params
        ).scalar() or 0.0

        processing_partners = conn.execute(
            text("SELECT COUNT(*) FROM acquirer")
        ).scalar() or 0

        payment_methods = conn.execute(
            text(f"""
                SELECT COUNT(DISTINCT t.credit_card_type)
                  FROM live_transactions t
                 {where_clause}
            """), base_params
        ).scalar() or 0

        geographic_regions = conn.execute(
            text("SELECT COUNT(DISTINCT country) FROM merchant")
        ).scalar() or 0

        fraud_rate = conn.execute(
            text(f"""
                SELECT COUNT(*) FILTER (WHERE t.fraud)*100.0/NULLIF(COUNT(*),0)
                  FROM live_transactions t
                 {where_clause}
            """), base_params
        ).scalar() or 0.0

        fraud_loss = conn.execute(
            text(f"""
                SELECT COALESCE(SUM(t.usd_value),0)
                  FROM live_transactions t
                 {where_clause} AND t.fraud = TRUE
            """), base_params
        ).scalar() or 0.0

        metrics += [
            {"title": "Total Transaction Volume",  "value": round(total_volume,   2)},
            {"title": "Average Transaction Value", "value": round(avg_value,      2)},
            {"title": "Processing Partners",       "value": processing_partners},
            {"title": "Payment Methods",           "value": payment_methods},
            {"title": "Geographic Regions",        "value": geographic_regions},
            {"title": "Fraud Rate (%)",            "value": round(fraud_rate,     2)},
            {"title": "Fraud Loss",                "value": round(fraud_loss,     2)},
        ]
        for m in metrics:
            m.setdefault("diff", 0.0)

        # ─── 1) Base charts ────────────────────────────────────
        for key, cfg in chart_configs.items():
            if key in (DRILL_LVL1, DRILL_LVL2):
                continue

            sql = cfg["sql"].format(
                join  = cfg.get("join", ""),
                where = where_clause
            )
            rows = conn.execute(text(sql), base_params).mappings().all()

            charts.append({
                "key":       key,
                "title":     cfg["title"],
                "type":      cfg["type"].value,
                "x":         [r["name"]         for r in rows],
                "y":         [float(r["value"]) for r in rows],
                "drillable": cfg["drillable"],
                "nextChart": cfg["next_chart"],
            })

        # If no base has been clicked yet, skip drill levels
        if not base_clicked:
            return {"metrics": metrics, "charts": charts}

        # Grab the config for the clicked base chart
        base_cfg = chart_configs[base_clicked]
        base_val = drill_keys[base_clicked]

        # ─── 2) Level 1 Drill ───────────────────────────────────
        lvl1_info = drill_keys.get(DRILL_LVL1, {})
        dim1      = lvl1_info.get("dimension")
        if dim1:
            # build join: include base_cfg.join and acquirer join if drilling on "name"
            join_parts = [base_cfg.get("join", "")]
            if dim1 == "name" and "JOIN acquirer" not in join_parts[0]:
                join_parts.append("JOIN acquirer a ON t.acquirer_id = a.id")
            join_sql = " ".join(p for p in join_parts if p)

            cfg1   = chart_configs[DRILL_LVL1]
            col1   = QUALIFIED_FIELDS.get(dim1, f"t.{dim1}")
            metric = base_cfg["metric"]

            sql1 = cfg1["sql"].format(
                join        = join_sql,
                where       = where_clause,
                dimension   = col1,
                metric      = metric,
                base_field  = base_cfg["drill_field"],
            )
            rows1 = conn.execute(
                text(sql1),
                {**base_params, "base_value": base_val}
            ).mappings().all()

            charts.append({
                "key":       DRILL_LVL1,
                "title":     cfg1["title"].format(
                                 dimension_label=ALL_DIMS.get(dim1, dim1),
                                 base_value=base_val
                             ),
                "type":      cfg1["type"].value,
                "x":         [r["name"]         for r in rows1],
                "y":         [float(r["value"]) for r in rows1],
                "drillable": cfg1["drillable"],
                "nextChart": cfg1["next_chart"],
            })

        # ─── 3) Level 2 Drill ───────────────────────────────────
        lvl1_val = lvl1_info.get("value")
        dim2     = drill_keys.get(DRILL_LVL2, {}).get("dimension")

        if dim1 and lvl1_val is not None and dim2:
            # build join
            join_parts = [base_cfg.get("join", "")]
            if (dim1 == "name" or dim2 == "name") and "JOIN acquirer" not in join_parts[0]:
                join_parts.append("JOIN acquirer a ON t.acquirer_id = a.id")
            join_sql = " ".join(p for p in join_parts if p)

            cfg2   = chart_configs[DRILL_LVL2]
            col2   = QUALIFIED_FIELDS.get(dim2, f"t.{dim2}")
            col1   = QUALIFIED_FIELDS.get(dim1, f"t.{dim1}")
            metric = base_cfg["metric"]

            sql2 = cfg2["sql"].format(
                join        = join_sql,
                where       = where_clause,
                dimension   = col2,
                metric      = metric,
                base_field  = base_cfg["drill_field"],
                lvl1_field  = col1,
            )
            rows2 = conn.execute(
                text(sql2),
                {
                    **base_params,
                    "base_value": base_val,
                    "lvl1_value": lvl1_val
                }
            ).mappings().all()

            charts.append({
                "key":       DRILL_LVL2,
                "title":     cfg2["title"].format(
                                 dimension_label=ALL_DIMS.get(dim2, dim2),
                                 lvl1_value=lvl1_val,
                                 lvl1_field_label=ALL_DIMS.get(dim1, dim1)
                             ),
                "type":      cfg2["type"].value,
                "x":         [r["name"]         for r in rows2],
                "y":         [float(r["value"]) for r in rows2],
                "drillable": cfg2["drillable"],
                "nextChart": cfg2["next_chart"],
            })

    return {"metrics": metrics, "charts": charts}
