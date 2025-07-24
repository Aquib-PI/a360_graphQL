import strawberry
from typing import Optional
from strawberry.scalars import JSON
from app.services.kpi_service import get_kpi_data
from app.gql_api.schema import FilterType, CustomRange, Dashboard, Chart

@strawberry.type
class Query:

    @strawberry.field
    def dashboard(
        self,
        filter_type: FilterType,
        custom: Optional[CustomRange] = None,
        drillKeys: Optional[JSON] = None,
    ) -> Dashboard:
        # drillKeys comes in as JSON—convert to a normal dict
        dk = drillKeys or {}
        raw = get_kpi_data(
            filter_type.value,
            (custom.start, custom.end) if custom else None,
            dk,
        )
        return Dashboard(
            charts=[
                Chart(
                    key=c["key"],
                    title=c["title"],
                    type=c["type"],
                    x=c["x"],
                    y=c["y"],
                    drillable=c["drillable"],
                    nextChart=c.get("nextChart"),
                )
                for c in raw["charts"]
            ]
        )
