import strawberry
from strawberry.scalars import JSON
from enum import Enum
from datetime import date
from typing import List, Optional, Tuple

import tiktoken
from scipy.stats import norm
import numpy as np

from app.services.fetch_dashboard import get_dashboard_data
from app.services.chart_configs import chart_configs
from app.LLM.grok_client import generate_grok_insight


# ── 1) Enums & Inputs ────────────────────────────────────────────────

@strawberry.enum
class FilterType(Enum):
    TODAY     = "TODAY"
    YESTERDAY = "YESTERDAY"
    DAILY     = "DAILY"
    WEEKLY    = "WEEKLY"
    MTD       = "MTD"
    MONTHLY   = "MONTHLY"
    YTD       = "YTD"
    CUSTOM    = "CUSTOM"

@strawberry.input
class CustomRange:
    start: date
    end:   date

@strawberry.enum
class ChartKey(Enum):
    REVENUE_BY_CURRENCY         = "revenueByCurrency"
    TOP_5_ACQUIRERS             = "top5Acquirers"
    PAYMENT_METHOD_DISTRIBUTION = "paymentMethodDistribution"


# ── 2) Dashboard DTOs ───────────────────────────────────────────────

@strawberry.type
class Metric:
    title: str
    value: float
    diff:  float

@strawberry.type
class Chart:
    key:       str
    title:     str
    type:      str
    x:         List[str]
    y:         List[float]
    drillable: bool
    nextChart: Optional[str]

@strawberry.type
class Dashboard:
    metrics: List[Metric]
    charts:  List[Chart]


# ── 3) Insight DTOs ────────────────────────────────────────────────

@strawberry.type
class TokenUsage:
    input_tokens:  int
    output_tokens: Optional[int]
    total_tokens:  Optional[int]

@strawberry.type
class ChartInsight:
    insight:     str
    token_usage: TokenUsage


# ── 4) Helpers ─────────────────────────────────────────────────────

def count_tokens(prompt: str, model: str = "gpt-3.5-turbo") -> int:
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(prompt))


def compare_to_historical_single_point(
    yesterday_val: float,
    historical_values: List[float],
    alpha: float = 0.05
) -> dict:
    n    = len(historical_values)
    mean = np.mean(historical_values) if n else 0.0
    std  = np.std(historical_values, ddof=1) if n > 1 else 0.0

    if std == 0:
        return {
            "z_score":        None,
            "p_value":        None,
            "mean":           round(mean, 2),
            "std":            round(std, 2),
            "is_significant": False,
            "insight":        "No variation in historical data."
        }

    z = (yesterday_val - mean) / std
    p = 2 * norm.sf(abs(z))

    t_multiplier = 1.96
    pred_margin  = t_multiplier * std * np.sqrt(1 + 1/n)
    lower        = mean - pred_margin
    upper        = mean + pred_margin
    is_outlier   = yesterday_val < lower or yesterday_val > upper

    summary = (
        f"Yesterday’s {yesterday_val:.2f} was "
        f"{'unusually high' if z > 0 else 'unusually low'} "
        f"vs historical mean {mean:.2f} (p={p:.4f})."
    ) if is_outlier else "Yesterday’s value was within the expected range."

    return {
        "z_score":        round(z, 2),
        "p_value":        round(p, 4),
        "mean":           round(mean, 2),
        "std":            round(std, 2),
        "is_significant": is_outlier,
        "insight":        summary
    }


def build_chart_insight_prompt(
    chart_title: str,
    dimension_label: str,
    data_pairs: List[Tuple[str, float]],
    stats: dict
) -> str:
    header = (
        f"You are a senior payments strategy analyst. Based on the **{chart_title}** chart below, "
        "provide a 60–80 word actionable business insight with strategic recommendations.\n\n"
    )

    top_lines = "\n".join([f"{name}: {value:.2f}" for name, value in data_pairs[:5]])

    stat_block = (
        f"\n\nHistorical mean: {stats['mean']:.2f}, std: {stats['std']:.2f}\n"
        f"Z-score: {stats['z_score']}, p-value: {stats['p_value']}\n"
        f"{stats['insight']}\n\n"
    )

    guidance = (
        "In your insight:\n"
        "- Highlight why any deviation is notable\n"
        "- Identify standout categories\n"
        "- Recommend a tactical action (e.g., rebalance volumes or test a new partner)\n"
        "- Call out any risks or what to monitor\n\n"
        f"Keep it high‑level and focused on {dimension_label}."
    )

    return header + top_lines + stat_block + guidance


# ── 5) Query Resolvers ───────────────────────────────────────────────

@strawberry.type
class Query:

    @strawberry.field
    def dashboard(
        self,
        filterType: FilterType,
        custom:     Optional[CustomRange] = None,
        drillKeys:  Optional[JSON]        = None,  # ← JSON scalar here
    ) -> Dashboard:
        raw = get_dashboard_data(
            filterType.value,
            (custom.start, custom.end) if custom else None,
            drillKeys or {}
        )
        return Dashboard(
            metrics=[Metric(**m) for m in raw["metrics"]],
            charts= [Chart(**c)    for c in raw["charts"   ]]
        )

    @strawberry.field
    def chart_insight(
        self,
        chartKey:   ChartKey,
        filterType: FilterType,
        custom:     Optional[CustomRange] = None,
    ) -> ChartInsight:
        raw = get_dashboard_data(
            filterType.value,
            (custom.start, custom.end) if (filterType == FilterType.CUSTOM and custom) else None,
            {}  # no drill for insight
        )

        chart = next((c for c in raw["charts"] if c["key"] == chartKey.value), None)
        if not chart:
            return ChartInsight(
                insight=f"No data for chart `{chartKey.value}`.",
                token_usage=TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0)
            )

        cfg         = chart_configs[chartKey.value]
        data_pairs  = list(zip(chart["x"], chart["y"]))
        yesterday   = data_pairs[0][1] if data_pairs else 0.0
        history     = [v for _, v in data_pairs[1:]]
        stats       = compare_to_historical_single_point(yesterday, history)
        prompt      = build_chart_insight_prompt(
            chart_title=cfg["title"],
            dimension_label=cfg["dimension_label"],
            data_pairs=data_pairs,
            stats=stats
        )
        input_tokens = count_tokens(prompt)

        try:
            resp          = generate_grok_insight(prompt, return_usage=True)
            text          = resp["text"]
            usage         = resp["usage"]
            output_tokens = usage.get("completion_tokens")
            total_tokens  = usage.get("total_tokens")
        except Exception as e:
            text          = f"Insight generation failed: {e}"
            output_tokens = None
            total_tokens  = None

        return ChartInsight(
            insight=text,
            token_usage=TokenUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens
            )
        )


schema = strawberry.Schema(query=Query)
