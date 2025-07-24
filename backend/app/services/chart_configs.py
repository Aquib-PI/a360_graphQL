from enum import Enum

class ChartType(Enum):
    PIE = "pie"
    BAR = "bar"

# Base chart keys
REVENUE_BY_CURRENCY         = "revenueByCurrency"
TOP_5_ACQUIRERS             = "top5Acquirers"
PAYMENT_METHOD_DISTRIBUTION = "paymentMethodDistribution"

# Drill levels
DRILL_LVL1 = "DRILL_LVL1"
DRILL_LVL2 = "DRILL_LVL2"

chart_configs = {
    # Level 0 charts
    REVENUE_BY_CURRENCY: {
        "title":           "Revenue by Currency",
        "type":            ChartType.PIE,
        "sql":             """
            SELECT t.transaction_currency AS name,
                   SUM(t.usd_value)           AS value
              FROM live_transactions t
             {where}
             GROUP BY t.transaction_currency
        """,
        "metric":          "SUM(t.usd_value)",
        "drillable":       True,
        "drill_field":     "t.transaction_currency",
        "next_chart":      DRILL_LVL1,
        "join":            "",
        "base_field":      "t.transaction_currency",
        "dimension_label": "Currency",
    },

    TOP_5_ACQUIRERS: {
        "title":           "Top 5 Acquirers by Volume",
        "type":            ChartType.BAR,
        "sql":             """
            SELECT a.name       AS name,
                   COUNT(*)      AS value
              FROM live_transactions t
             {join}
             {where}
             GROUP BY a.name
             ORDER BY value DESC
             LIMIT 5
        """,
        "metric":          "COUNT(*)",
        "drillable":       True,
        "drill_field":     "a.name",
        "next_chart":      DRILL_LVL1,
        "join":            "JOIN acquirer a ON t.acquirer_id = a.id",
        "base_field":      "a.name",
        "dimension_label": "Acquirer",
    },

    PAYMENT_METHOD_DISTRIBUTION: {
        "title":           "Payment Method Distribution",
        "type":            ChartType.BAR,
        "sql":             """
            SELECT t.credit_card_type AS name,
                   COUNT(*)            AS value
              FROM live_transactions t
             {where}
             GROUP BY t.credit_card_type
        """,
        "metric":          "COUNT(*)",
        "drillable":       True,
        "drill_field":     "t.credit_card_type",
        "next_chart":      DRILL_LVL1,
        "join":            "",
        "base_field":      "t.credit_card_type",
        "dimension_label": "Payment Method",
    },

    # Level 1 drill
    DRILL_LVL1: {
        "title":           "{dimension_label} breakdown for {base_value}",
        "type":            ChartType.BAR,
        "sql":             """
            SELECT {dimension}    AS name,
                   {metric}       AS value
              FROM live_transactions t
             {join}
             {where}
               AND {base_field} = :base_value
             GROUP BY {dimension}
        """,
        "drillable":       True,
        "drill_field":     None,
        "next_chart":      DRILL_LVL2,
    },

    # Level 2 drill
    DRILL_LVL2: {
        "title":           "{dimension_label} breakdown for {lvl1_value} ({lvl1_field_label})",
        "type":            ChartType.BAR,
        "sql":             """
            SELECT {dimension}    AS name,
                   {metric}       AS value
              FROM live_transactions t
             {join}
             {where}
               AND {base_field} = :base_value
               AND {lvl1_field} = :lvl1_value
             GROUP BY {dimension}
        """,
        "drillable":       False,
        "drill_field":     None,
        "next_chart":      None,
    },
}
