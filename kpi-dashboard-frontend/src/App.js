// src/App.js
import React, { useState } from "react";
import { ApolloProvider, useLazyQuery } from "@apollo/client";

import { client }         from "./apolloClient";
import { useDashboard }   from "./hooks/useDashboard";
import { ChartContainer } from "./components/ChartContainer";
import { ContextMenu }    from "./components/ContextMenu";
import { CHART_INSIGHT }  from "./graphql/queries";

// ── Constants ─────────────────────────────────────────────────────────
const DIMENSIONS = [
  { label: "Card Type", value: "credit_card_type" },
  { label: "Currency",  value: "transaction_currency" },
  { label: "Acquirer",  value: "name" },
];
const LEVEL1 = "DRILL_LVL1";
const LEVEL2 = "DRILL_LVL2";

// ── Helpers ───────────────────────────────────────────────────────────

// Convert camelCase chart key → UPPER_SNAKE_CASE enum literal
function toEnumKey(camel) {
  return camel.replace(/([A-Z])/g, "_$1").toUpperCase();
}

// Render a back‑button
const backButtonStyle = {
  marginBottom: 12,
  padding: "6px 12px",
  border: "1px solid #ccc",
  borderRadius: 4,
  backgroundColor: "#f9f9f9",
  cursor: "pointer",
};
function renderBack(onClick, label) {
  return (
    <button onClick={onClick} style={backButtonStyle}>
      ← Back to {label}
    </button>
  );
}

// Centered loading / error message
function CenteredMessage({ text, retry = false }) {
  return (
    <div style={{ padding: 20, textAlign: "center" }}>
      <p>{text}</p>
      {retry && (
        <button onClick={() => window.location.reload()} style={{ marginTop: 10 }}>
          Retry
        </button>
      )}
    </div>
  );
}

// ── DrillSection Component ────────────────────────────────────────────
function DrillSection({ baseKey, charts, drillKeys, setDrillKeys, filterType }) {
  // Hooks must be called unconditionally at top
  const [contextMenu, setContextMenu] = useState(null);
  const [getInsight, { data: insightData, loading: insightLoading, error: insightError }] =
    useLazyQuery(CHART_INSIGHT, { fetchPolicy: "no-cache" });

  // Find Level 0, 1, 2 charts
  const baseChart = charts.find((c) => c.key === baseKey);
  if (!baseChart) return null;

  const lvl1Key   = baseChart.nextChart;
  const lvl1Chart = charts.find((c) => c.key === lvl1Key) || null;
  const lvl2Key   = lvl1Chart?.nextChart;
  const lvl2Chart = charts.find((c) => c.key === lvl2Key) || null;

  const baseVal = drillKeys[baseKey] || null;
  const lvl1    = drillKeys[lvl1Key] || {};
  const lvl2    = drillKeys[lvl2Key] || {};

  const atLevel1 = baseVal && lvl1.dimension && !lvl1.value;
  const atLevel2 = lvl1.value && lvl2.dimension && !lvl2.value;

  // Drill click handlers
  const onBaseClick = (e, name) =>
    setContextMenu({ x: e.clientX, y: e.clientY, sliceName: name, level: "base", excludeDimension: null });

  const onLvl1Click = (e, name) =>
    setContextMenu({ x: e.clientX, y: e.clientY, sliceName: name, level: "lvl1", excludeDimension: lvl1.dimension });

  const onLvl2Click = (e, name) =>
    setDrillKeys((prev) => ({ ...prev, [lvl2Key]: { dimension: lvl2.dimension, value: name } }));

  const handleDimensionSelect = (dim) => {
    if (contextMenu.level === "base") {
      setDrillKeys({
        [baseKey]: contextMenu.sliceName,
        [lvl1Key]: { dimension: dim, value: null },
      });
    } else {
      setDrillKeys((prev) => ({
        ...prev,
        [lvl1Key]: { dimension: lvl1.dimension, value: contextMenu.sliceName },
        [lvl2Key]: { dimension: dim, value: null },
      }));
    }
    setContextMenu(null);
  };

  // Determine which chart to show & its onDrill handler
  let chartToShow = baseChart;
  let onDrill     = onBaseClick;
  if (atLevel2 && lvl2Chart) {
    chartToShow = lvl2Chart;
    onDrill     = onLvl2Click;
  } else if (atLevel1 && lvl1Chart) {
    chartToShow = lvl1Chart;
    onDrill     = onLvl1Click;
  }

  // Back button logic
  let backButton = null;
  if (atLevel2) {
    backButton = renderBack(() => {
      const nk = { ...drillKeys };
      delete nk[lvl2Key];
      setDrillKeys(nk);
    }, lvl1.value);
  } else if (atLevel1) {
    backButton = renderBack(() => {
      const nk = { ...drillKeys };
      delete nk[lvl1Key];
      setDrillKeys(nk);
    }, "Overview");
  }

  return (
    <div style={{ margin: 20, padding: 16, border: "1px solid #eee", borderRadius: 8 }}>
      {backButton}

      {/* Title + AI button */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3>{chartToShow.title}</h3>
        <button
          onClick={() => {
            const enumKey = toEnumKey(baseKey);
            getInsight({ variables: { chartKey: enumKey, filterType } });
          }}
          disabled={insightLoading}
          style={{
            padding: "6px 12px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          {insightLoading ? "Thinking…" : "AI"}
        </button>
      </div>

      {/* ECharts container */}
      <ChartContainer chart={chartToShow} onDrill={onDrill} key={chartToShow.key} />

      {/* AI Insight */}
      {insightError && <p style={{ color: "red" }}>Error: {insightError.message}</p>}
      {insightData?.chartInsight?.insight && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            backgroundColor: "#f8f9fa",
            borderLeft: "4px solid #007bff",
          }}
        >
          <strong>AI Insight:</strong>
          <p>{insightData.chartInsight.insight}</p>
          <small style={{ color: "#666" }}>
            Tokens in {insightData.chartInsight.tokenUsage.inputTokens}, out{" "}
            {insightData.chartInsight.tokenUsage.outputTokens}, total{" "}
            {insightData.chartInsight.tokenUsage.totalTokens}
          </small>
        </div>
      )}

      {/* Drill context menu */}
      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          sliceName={contextMenu.sliceName}
          dimensions={DIMENSIONS}
          excludeDimension={contextMenu.excludeDimension}
          onClose={() => setContextMenu(null)}
          onSelect={handleDimensionSelect}
        />
      )}
    </div>
  );
}

// ── DashboardPage ───────────────────────────────────────────────────
function DashboardPage() {
  const [drillKeys, setDrillKeys] = useState({});
  const { data, loading, error } = useDashboard("YTD", null, drillKeys);

  if (loading) return <CenteredMessage text="Loading dashboard…" />;
  if (error)   return <CenteredMessage text={`Error: ${error.message}`} retry />;
  if (!data?.dashboard) return <CenteredMessage text="No data" />;

  const { charts } = data.dashboard;
  const baseKeys = charts.map((c) => c.key).filter((k) => k !== LEVEL1 && k !== LEVEL2);

  return (
    <div style={{ padding: 20, maxWidth: 1200, margin: "auto" }}>
      <h1>Dashboard</h1>
      {baseKeys.map((key) => (
        <DrillSection
          key={key}
          baseKey={key}
          charts={charts}
          drillKeys={drillKeys}
          setDrillKeys={setDrillKeys}
          filterType="YTD"
        />
      ))}
    </div>
  );
}

// ── App Entry ────────────────────────────────────────────────────────
export default function App() {
  return (
    <ApolloProvider client={client}>
      <DashboardPage />
    </ApolloProvider>
  );
}
