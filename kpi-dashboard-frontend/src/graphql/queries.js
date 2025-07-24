import { gql } from "@apollo/client";

export const CHART_INSIGHT = gql`
  query ChartInsight($chartKey: ChartKey!, $filterType: FilterType!) {
    chartInsight(chartKey: $chartKey, filterType: $filterType) {
      insight
      tokenUsage {
        inputTokens
        outputTokens
        totalTokens
      }
    }
  }
`;
