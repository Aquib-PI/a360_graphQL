"use client"

import { useState } from "react"
import { ApolloProvider } from "@apollo/client"
import { client } from "./apolloClient"
import { useDashboard } from "./hooks/useDashboard"
import { ChartContainer } from "./components/ChartContainer"
import { ContextMenu } from "./components/ContextMenu"

const DIMENSIONS = [
  { label: "Card Type", value: "credit_card_type" },
  { label: "Currency", value: "transaction_currency" },
  { label: "Acquirer", value: "name" },
]

const LEVEL1 = "DRILL_LVL1"
const LEVEL2 = "DRILL_LVL2"

// A simple centered message with optional retry button
function CenteredMessage({ text, retry = false }) {
  return (
    <div style={{ padding: 20, textAlign: "center" }}>
      <p>{text}</p>
      {retry && (
        <button onClick={() => window.location.reload()} style={{ marginTop: 10, padding: "6px 12px" }}>
          Retry
        </button>
      )}
    </div>
  )
}

// Utility to render a back‑button
function renderBack(onClick, label) {
  return (
    <button onClick={onClick} style={backButtonStyle}>
      ← Back to {label}
    </button>
  )
}

// Shared styles
const metricCardStyle = {
  flex: "1 1 200px",
  minWidth: 200,
  padding: 16,
  border: "1px solid #ddd",
  borderRadius: 8,
  backgroundColor: "white",
  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
}
const metricTitleStyle = { marginBottom: 8, fontSize: 14, color: "#666" }
const metricValueStyle = { fontSize: "1.5em", fontWeight: "bold" }
const diffStyle = { marginLeft: 8, color: "#4caf50", fontSize: "0.7em" }
const resetButtonStyle = {
  padding: "10px 20px",
  backgroundColor: "#007bff",
  color: "white",
  border: "none",
  borderRadius: 4,
  cursor: "pointer",
  fontSize: 14,
}
const backButtonStyle = {
  marginBottom: 12,
  padding: "6px 12px",
  border: "1px solid #ccc",
  borderRadius: 4,
  backgroundColor: "#f9f9f9",
  cursor: "pointer",
}

// The per‑chart section with pending logic and back buttons
function DrillSection({ baseKey, charts, drillKeys, setDrillKeys }) {
  // 🚨 Always call hooks first:
  const [contextMenu, setContextMenu] = useState(null)

  // Then bail out early if no base chart
  const baseChart = charts.find((c) => c.key === baseKey)
  if (!baseChart) return null

  // Derive L1 and L2 keys & charts
  const lvl1Key = baseChart.nextChart
  const lvl1Chart = charts.find((c) => c.key === lvl1Key) || null
  const lvl2Key = lvl1Chart?.nextChart
  const lvl2Chart = charts.find((c) => c.key === lvl2Key) || null

  // Confirmed drill state from backend
  const baseVal = drillKeys[baseKey] || null
  const lvl1 = drillKeys[lvl1Key] || {}
  const lvl2 = drillKeys[lvl2Key] || {}

  // Helpers to detect where we are
  const atLevel1 = baseVal && lvl1.dimension && lvl1.value && !lvl2.dimension
  const atLevel2 = baseVal && lvl1.dimension && lvl1.value && lvl2.dimension && lvl2.value

  //
  // 1) Pie‐slice clicks show context menu with dimension selection
  //
  const onBaseClick = (event, name) => {
    console.log("=== BASE CLICK HANDLER ===")
    console.log("Event:", event)
    console.log("Name:", name)

    if (name) {
      // Handle both regular DOM events and synthetic events
      const x = event.clientX || event.pageX || 100
      const y = event.clientY || event.pageY || 100

      console.log("Setting context menu at:", { x, y })

      setContextMenu({
        x: x,
        y: y,
        sliceName: name,
        level: "base",
        excludeDimension: null,
      })

      console.log("Context menu state set!")
    } else {
      console.log("No name provided, not setting context menu")
    }
    console.log("=== END BASE CLICK HANDLER ===")
  }

  const onLvl1Click = (event, name) => {
    console.log("=== LEVEL 1 CLICK HANDLER ===")
    console.log("Event:", event)
    console.log("Name:", name)

    if (name) {
      // Handle both regular DOM events and synthetic events
      const x = event.clientX || event.pageX || 100
      const y = event.clientY || event.pageY || 100

      setContextMenu({
        x: x,
        y: y,
        sliceName: name,
        level: "lvl1",
        excludeDimension: lvl1.dimension, // Exclude the dimension already used in level 1
      })
    }
    console.log("=== END LEVEL 1 CLICK HANDLER ===")
  }

  // Level 2 click handler to set the final value
  const onLvl2Click = (event, name) => {
    console.log("=== LEVEL 2 CLICK HANDLER ===")
    console.log("Event:", event)
    console.log("Name:", name)

    if (name) {
      // Set the final level 2 value
      setDrillKeys((prev) => ({
        ...prev,
        [lvl2Key]: { ...prev[lvl2Key], value: name },
      }))
      console.log("Level 2 value set:", name)
    }
    console.log("=== END LEVEL 2 CLICK HANDLER ===")
  }

  //
  // 2) Dimension selection from context menu - FIXED LOGIC
  //
  const handleDimensionSelect = (selectedDimension) => {
    console.log("=== DIMENSION SELECT ===")
    console.log("Selected dimension:", selectedDimension)
    console.log("Context menu state:", contextMenu)

    if (contextMenu) {
      if (contextMenu.level === "base") {
        console.log("Setting base drill keys...")
        // FIXED: Set base value (the clicked slice name) and level 1 dimension (selected from menu)
        // The level 1 value will be set when user clicks on the level 1 chart
        setDrillKeys({
          [baseKey]: contextMenu.sliceName,
          [lvl1Key]: { dimension: selectedDimension, value: null },
        })
      } else if (contextMenu.level === "lvl1") {
        console.log("Setting level 2 drill keys...")
        // FIXED: Set level 1 value (the clicked slice name) and level 2 dimension (selected from menu)
        // The level 2 value will be set when user clicks on the level 2 chart
        setDrillKeys((prev) => ({
          ...prev,
          [lvl1Key]: { ...prev[lvl1Key], value: contextMenu.sliceName },
          [lvl2Key]: { dimension: selectedDimension, value: null },
        }))
      }
      setContextMenu(null)
      console.log("Context menu closed")
    }
    console.log("=== END DIMENSION SELECT ===")
  }

  //
  // Decide which chart to render - FIXED LOGIC
  //
  let chartToShow = null
  let onDrill = null

  // --- Level 2 complete: show final L2 chart ---
  if (atLevel2) {
    chartToShow = lvl2Chart
    onDrill = null // No more drilling
    console.log("State: Level 2 complete - showing final L2 chart")
    // --- Level 2 dimension set, waiting for L2 value: show L2 chart clickable ---
  } else if (lvl1.value && lvl2.dimension && !lvl2.value && lvl2Chart) {
    chartToShow = lvl2Chart
    onDrill = onLvl2Click
    console.log("State: L2 dimension set, waiting for L2 value - showing L2 chart clickable")
    // --- Level 1 dimension set, waiting for L1 value: show L1 chart clickable ---
  } else if (baseVal && lvl1.dimension && !lvl1.value && lvl1Chart) {
    chartToShow = lvl1Chart
    onDrill = onLvl1Click
    console.log("State: L1 dimension set, waiting for L1 value - showing L1 chart clickable")
    // --- No drill yet: show base chart clickable ---
  } else {
    chartToShow = baseChart
    onDrill = onBaseClick
    console.log("State: No drill - showing base chart")
  }

  console.log("Current drill state:", {
    baseVal,
    lvl1Dimension: lvl1.dimension,
    lvl1Value: lvl1.value,
    lvl2Dimension: lvl2.dimension,
    lvl2Value: lvl2.value,
    atLevel1,
    atLevel2,
    chartToShow: chartToShow?.key,
    hasOnDrill: !!onDrill,
  })

  console.log("Drill keys being sent to backend:", drillKeys)

  //
  // Back button logic
  //
  let backButton = null
  if (atLevel2) {
    // Back from L2 → L1
    backButton = renderBack(() => {
      const newKeys = { ...drillKeys }
      delete newKeys[lvl2Key]
      setDrillKeys(newKeys)
    }, lvl1.value || "Level 1")
  } else if (atLevel1) {
    // Back from L1 → Overview
    backButton = renderBack(() => {
      const newKeys = { ...drillKeys }
      delete newKeys[lvl1Key]
      setDrillKeys(newKeys)
    }, "Overview")
  }

  return (
    <div style={{ marginBottom: 60, padding: 16, border: "1px solid #eee", borderRadius: 8, position: "relative" }}>
      {backButton}

      {/* Enhanced Debug info */}
      <div
        style={{
          fontSize: "11px",
          color: "#666",
          marginBottom: "10px",
          padding: "8px",
          backgroundColor: "#f0f0f0",
          borderRadius: "4px",
        }}
      >
        <strong>Debug Info:</strong>
        <br />
        Chart: {chartToShow?.key} | OnDrill: {onDrill ? "YES" : "NO"} | BaseVal: {baseVal || "none"}
        <br />
        L1: {lvl1.dimension || "none"}/{lvl1.value || "none"} | L2: {lvl2.dimension || "none"}/{lvl2.value || "none"}
        <br />
        AtLevel1: {atLevel1 ? "YES" : "NO"} | AtLevel2: {atLevel2 ? "YES" : "NO"}
        <br />
        Context Menu: {contextMenu ? `Open at (${contextMenu.x}, ${contextMenu.y})` : "Closed"}
        <br />
        <strong>Drill Keys:</strong> {JSON.stringify(drillKeys, null, 2)}
      </div>

      {chartToShow && (
        <ChartContainer
          chart={chartToShow}
          onDrill={onDrill}
          key={[
            chartToShow.key,
            drillKeys[baseKey] || "",
            drillKeys[lvl1Key]?.dimension || "",
            drillKeys[lvl1Key]?.value || "",
            drillKeys[lvl2Key]?.dimension || "",
            drillKeys[lvl2Key]?.value || "",
          ].join("|")}
        />
      )}

      {/* Context Menu */}
      {contextMenu && (
        <div>
          <div style={{ fontSize: "10px", color: "red", marginBottom: "5px" }}>
            Context Menu Active: {contextMenu.sliceName} at ({contextMenu.x}, {contextMenu.y})
          </div>
          <ContextMenu
            x={contextMenu.x}
            y={contextMenu.y}
            sliceName={contextMenu.sliceName}
            dimensions={DIMENSIONS}
            excludeDimension={contextMenu.excludeDimension}
            onClose={() => {
              console.log("Context menu closed by user")
              setContextMenu(null)
            }}
            onSelect={handleDimensionSelect}
          />
        </div>
      )}
    </div>
  )
}

//
// DashboardPage
//
function DashboardPage() {
  const [drillKeys, setDrillKeys] = useState({})
  const { data, loading, error } = useDashboard("YTD", null, drillKeys)

  if (loading) return <CenteredMessage text="Loading dashboard..." />
  if (error) return <CenteredMessage text={`Error: ${error.message}`} retry />
  if (!data?.dashboard) return <CenteredMessage text="No dashboard data available" />

  const { metrics = [], charts = [] } = data.dashboard

  // Render your metrics at the top
  const metricsBlock = metrics.length > 0 && (
    <div style={{ display: "flex", gap: 20, marginBottom: 40, flexWrap: "wrap" }}>
      {metrics.map((m, i) => (
        <div key={m.title || i} style={metricCardStyle}>
          <h4 style={metricTitleStyle}>{m.title || "Metric"}</h4>
          <div style={metricValueStyle}>
            {typeof m.value === "number" ? m.value.toLocaleString() : m.value || "N/A"}
            {typeof m.diff === "number" && (
              <small style={diffStyle}>
                ({m.diff >= 0 ? "+" : ""}
                {m.diff}%)
              </small>
            )}
          </div>
        </div>
      ))}
    </div>
  )

  // Top‐level chart keys
  const baseKeys = charts.map((c) => c.key).filter((k) => k && k !== LEVEL1 && k !== LEVEL2)

  return (
    <div style={{ padding: 20, maxWidth: 1200, margin: "auto" }}>
      <h1 style={{ marginBottom: 30 }}>Dashboard</h1>
      {metricsBlock}
      <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
        {baseKeys.map((key) => (
          <DrillSection key={key} baseKey={key} charts={charts} drillKeys={drillKeys} setDrillKeys={setDrillKeys} />
        ))}
      </div>
      {Object.keys(drillKeys).length > 0 && (
        <div style={{ textAlign: "center", marginTop: 40 }}>
          <button onClick={() => setDrillKeys({})} style={resetButtonStyle}>
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  )
}

export default function App() {
  return (
    <ApolloProvider client={client}>
      <DashboardPage />
    </ApolloProvider>
  )
}
