import { gql, useQuery } from "@apollo/client";

const DASHBOARD_QUERY = gql`
  query Dashboard(
    $filterType: FilterType!,
    $custom:     CustomRange,
    $drillKeys:  JSON
  ) {
    dashboard(filterType: $filterType, custom: $custom, drillKeys: $drillKeys) {
      metrics {
        title
        value
        diff
      }
      charts {
        key
        title
        type
        x
        y
        drillable
        nextChart
      }
    }
  }
`;

export function useDashboard(filterType, custom, drillKeys) {
  const variables = {
    filterType,
    custom: filterType === "CUSTOM" ? custom : null,
    drillKeys,
  };
  return useQuery(DASHBOARD_QUERY, { variables, fetchPolicy: "network-only" });
}
