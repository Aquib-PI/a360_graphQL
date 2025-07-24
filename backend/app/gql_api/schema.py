# app/graphql/schema.py
import strawberry
from enum import Enum
from datetime import date
from typing import List, Optional
from strawberry.scalars import JSON
from app.services.fetch_dashboard import get_dashboard_data

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

@strawberry.type
class Metric:
    title: str
    value: float
    diff: float

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

@strawberry.type
class Query:
    @strawberry.field
    def dashboard(
        self,
        filterType: FilterType,
        custom:     Optional[CustomRange] = None,
        drillKeys:  Optional[JSON]        = None,
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

schema = strawberry.Schema(query=Query)
