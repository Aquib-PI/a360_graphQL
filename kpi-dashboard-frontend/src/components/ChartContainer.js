import { useId } from "react"
import ReactEcharts from "echarts-for-react"

export function ChartContainer({ chart, onDrill }) {
  // 1) Generate a unique ID for this instance and sanitize it
  const rawId = useId()
  const echartsId = rawId.replace(/[^a-zA-Z0-9-_]/g, "") || `chart-${Math.random().toString(36).substr(2, 9)}`

  const { title, type, x = [], y = [], drillable } = chart

  console.log("ChartContainer rendered:", {
    title,
    type,
    drillable,
    hasOnDrill: !!onDrill,
    xLength: x.length,
    yLength: y.length,
    rawId,
    sanitizedId: echartsId,
    finalChartId: `echarts-${echartsId}`,
  })

  // 2) Build either a pie or an axis-based option
  const option =
    type === "pie"
      ? {
          title: { text: title, left: "center" },
          tooltip: { trigger: "item" },
          legend: { orient: "horizontal", top: 25 },
          series: [
            {
              type: "pie",
              radius: "60%",
              data: x.map((name, i) => ({ name, value: y[i] })),
              label: { formatter: "{b}: {d}%" },
            },
          ],
        }
      : {
          title: { text: title, left: "center" },
          tooltip: { trigger: "axis" },
          xAxis: { type: "category", data: x },
          yAxis: { type: "value" },
          series: [
            {
              type,
              data: y,
              label: { show: true, position: "top" },
            },
          ],
        }

  // 3) Enhanced drill handler for context menu
  const onChartClick = (params, echartInstance) => {
    console.log("=== CHART CLICK EVENT ===")
    console.log("Click params:", params)
    console.log("Chart drillable:", drillable)
    console.log("onDrill function exists:", !!onDrill)
    console.log("Params name:", params?.name)
    console.log("Chart ID:", `echarts-${echartsId}`)

    if (onDrill && params?.name) {
      console.log("Attempting to call onDrill...")

      // Get the chart container element
      const chartContainer = document.getElementById(`echarts-${echartsId}`)
      console.log("Chart container found:", !!chartContainer)

      if (chartContainer) {
        const rect = chartContainer.getBoundingClientRect()
        console.log("Container rect:", rect)

        // Create a synthetic event object with coordinates
        const syntheticEvent = {
          clientX: rect.left + rect.width / 2,
          clientY: rect.top + rect.height / 2,
          pageX: rect.left + rect.width / 2,
          pageY: rect.top + rect.height / 2,
          currentTarget: chartContainer,
          preventDefault: () => {},
          stopPropagation: () => {},
        }

        console.log("Calling onDrill with synthetic event:", syntheticEvent)
        console.log("Slice name:", params.name)

        try {
          onDrill(syntheticEvent, params.name)
          console.log("onDrill called successfully!")
        } catch (error) {
          console.error("Error calling onDrill:", error)
        }
      } else {
        console.error("Chart container not found for ID:", `echarts-${echartsId}`)

        // Fallback: try to find any chart container and use window coordinates
        console.log("Attempting fallback with window coordinates...")
        const fallbackEvent = {
          clientX: window.innerWidth / 2,
          clientY: window.innerHeight / 2,
          pageX: window.innerWidth / 2,
          pageY: window.innerHeight / 2,
          currentTarget: null,
          preventDefault: () => {},
          stopPropagation: () => {},
        }

        try {
          onDrill(fallbackEvent, params.name)
          console.log("onDrill called successfully with fallback coordinates!")
        } catch (error) {
          console.error("Error calling onDrill with fallback:", error)
        }
      }
    } else {
      console.log("Click not processed because:")
      console.log("- onDrill exists:", !!onDrill)
      console.log("- params.name exists:", !!params?.name)
      console.log("- drillable flag:", drillable)
    }
    console.log("=== END CHART CLICK EVENT ===")
  }

  return (
    <div style={{ marginBottom: 40 }}>
      {/* Debug info above chart */}
      <div
        style={{
          fontSize: "10px",
          color: "#999",
          marginBottom: "5px",
          padding: "5px",
          backgroundColor: "#f9f9f9",
          border: "1px solid #eee",
        }}
      >
        Chart Debug: ID={`echarts-${echartsId}`}, Drillable={drillable ? "YES" : "NO"}, OnDrill={onDrill ? "YES" : "NO"}
        , Type={type}
      </div>

      <ReactEcharts
        // 👇 each instance gets its own DOM node with sanitized ID
        id={`echarts-${echartsId}`}
        option={option}
        style={{ height: "350px", width: "100%" }}
        onEvents={{
          click: onChartClick,
          // Add more event listeners for debugging
          mouseover: (params) => console.log("Mouse over:", params?.name),
          mouseout: (params) => console.log("Mouse out:", params?.name),
        }}
      />
    </div>
  )
}
