"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useEffect, useState } from "react"

function generateData(points: number) {
  const data: number[] = []
  let val = 50
  for (let i = 0; i < points; i++) {
    val += (Math.random() - 0.5) * 12
    val = Math.max(10, Math.min(90, val))
    data.push(val)
  }
  return data
}

export function TelemetryChart({
  label,
  height = 64,
}: {
  label: string
  height?: number
}) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true })
  const [data, setData] = useState<number[]>([])
  const points = 50

  useEffect(() => {
    setData(generateData(points))
  }, [])

  useEffect(() => {
    if (!isInView) return
    const interval = setInterval(() => {
      setData((prev) => {
        const next = [...prev.slice(1)]
        let last = prev[prev.length - 1] || 50
        last += (Math.random() - 0.5) * 8
        last = Math.max(10, Math.min(90, last))
        next.push(last)
        return next
      })
    }, 300)
    return () => clearInterval(interval)
  }, [isInView])

  const width = 100
  const pathD = data
    .map((val, i) => {
      const x = (i / (points - 1)) * width
      const y = height - (val / 100) * height
      return `${i === 0 ? "M" : "L"} ${x} ${y}`
    })
    .join(" ")

  return (
    <div ref={ref} className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] tracking-[0.15em] text-muted-foreground uppercase">
          {label}
        </span>
        <span className="font-mono text-[10px] text-muted-foreground tabular-nums">
          {data.length > 0 ? data[data.length - 1]?.toFixed(1) : "--"}
        </span>
      </div>
      <div className="overflow-hidden">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="none"
          className="w-full"
          style={{ height }}
        >
          {/* Baseline */}
          <line x1={0} y1={height / 2} x2={width} y2={height / 2} stroke="rgba(255,255,255,0.03)" strokeWidth={0.5} />
          {/* Line */}
          {data.length > 1 && (
            <motion.path
              d={pathD}
              fill="none"
              stroke="rgba(255,255,255,0.35)"
              strokeWidth={0.8}
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: 0 }}
              animate={isInView ? { pathLength: 1 } : {}}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />
          )}
        </svg>
      </div>
    </div>
  )
}
