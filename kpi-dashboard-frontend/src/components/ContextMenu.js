"use client"

import { useEffect, useRef } from "react"

const contextMenuStyle = {
  position: "fixed",
  backgroundColor: "white",
  border: "1px solid #e0e0e0",
  borderRadius: "8px",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
  padding: "16px",
  minWidth: "280px",
  zIndex: 1000,
}

const headerStyle = {
  marginBottom: "12px",
  fontSize: "14px",
  color: "#333",
  fontWeight: "normal",
}

const buttonContainerStyle = {
  display: "flex",
  gap: "8px",
  flexWrap: "wrap",
}

const dimensionButtonStyle = {
  padding: "8px 16px",
  border: "1px solid #ddd",
  borderRadius: "4px",
  backgroundColor: "white",
  cursor: "pointer",
  fontSize: "14px",
  color: "#333",
  transition: "all 0.2s",
}

const dimensionButtonHoverStyle = {
  ...dimensionButtonStyle,
  backgroundColor: "#f5f5f5",
  borderColor: "#007bff",
}

export function ContextMenu({ x, y, onClose, onSelect, sliceName, dimensions, excludeDimension = null }) {
  const menuRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        onClose()
      }
    }

    const handleEscape = (event) => {
      if (event.key === "Escape") {
        onClose()
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    document.addEventListener("keydown", handleEscape)

    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
      document.removeEventListener("keydown", handleEscape)
    }
  }, [onClose])

  // Adjust position to keep menu within viewport
  const adjustedStyle = {
    ...contextMenuStyle,
    left: Math.min(x, window.innerWidth - 300),
    top: Math.min(y, window.innerHeight - 200),
  }

  // Filter out excluded dimension if provided
  const availableDimensions = excludeDimension 
    ? dimensions.filter(d => d.value !== excludeDimension)
    : dimensions

  return (
    <div ref={menuRef} style={adjustedStyle}>
      <div style={headerStyle}>
        You selected "<strong>{sliceName}</strong>". Choose a breakdown dimension:
      </div>
      <div style={buttonContainerStyle}>
        {availableDimensions.map((dimension) => (
          <button
            key={dimension.value}
            style={dimensionButtonStyle}
            onMouseEnter={(e) => {
              Object.assign(e.currentTarget.style, dimensionButtonHoverStyle)
            }}
            onMouseLeave={(e) => {
              Object.assign(e.currentTarget.style, dimensionButtonStyle)
            }}
            onClick={() => {
              onSelect(dimension.value)
              onClose()
            }}
          >
            {dimension.label}
          </button>
        ))}
      </div>
    </div>
  )
}
