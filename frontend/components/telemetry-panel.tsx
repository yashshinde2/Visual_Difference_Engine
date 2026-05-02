"use client"

import { motion, useInView } from "framer-motion"
import { useRef, useEffect, useState, useContext } from "react"
import { BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from "recharts"
import { SectionHeader } from "./section-header"
import { AnalysisContext } from "@/app/page"

function ProgressMetric({
  label,
  value,
  index,
}: {
  label: string
  value: number
  index: number
}) {
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true })
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    if (!isInView) return
    const duration = 1200
    const startTime = performance.now()
    function tick(now: number) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplayValue(Math.round(value * eased))
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [isInView, value])

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      className="flex flex-col gap-2"
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-[10px] tracking-[0.15em] text-muted-foreground uppercase">
          {label}
        </span>
        <span className="font-mono text-xs text-foreground tabular-nums">
          {displayValue}%
        </span>
      </div>
      <div className="h-px w-full bg-border">
        <motion.div
          className="h-px bg-foreground/50"
          initial={{ width: "0%" }}
          animate={isInView ? { width: `${value}%` } : {}}
          transition={{ duration: 1.2, ease: "easeOut", delay: index * 0.08 }}
        />
      </div>
    </motion.div>
  )
}

function MetricValue({
  label,
  value,
  unit,
  index,
}: {
  label: string
  value: string
  unit: string
  index: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4, delay: index * 0.08 }}
      className="flex flex-col gap-1"
    >
      <span className="font-mono text-[10px] tracking-[0.15em] text-muted-foreground/50 uppercase">
        {label}
      </span>
      <div className="flex items-baseline gap-1">
        <span className="font-mono text-lg font-light text-foreground tabular-nums">{value}</span>
        <span className="font-mono text-[10px] text-muted-foreground">{unit}</span>
      </div>
    </motion.div>
  )
}

export function TelemetryPanel() {
  const context = useContext(AnalysisContext)
  const analysisResult = context?.analysisResult

  const scores = analysisResult?.metrics || {}
  
  // Extract scores safely with proper fallbacks
  const ssimScore = typeof scores.ssim_score === 'number' ? scores.ssim_score : 0
  const ssimPercent = typeof scores.ssim_percent === 'number' ? scores.ssim_percent : ssimScore * 100
  const severity = typeof scores.severity === 'number' ? scores.severity : 0
  const confidence = typeof scores.confidence === 'number' ? scores.confidence : 0
  const differencePercent = typeof scores.difference_percentage === 'number' ? scores.difference_percentage : 0
  const anomalyScore = typeof scores.anomaly_score === 'number' ? scores.anomaly_score : 0
  const mse = typeof scores.mse === 'number' ? scores.mse : 0

  if (!analysisResult) {
    return (
      <section className="relative px-6 py-32">
        <SectionHeader
          label="03"
          title="TELEMETRY"
          subtitle="Real-time performance metrics"
        />

        <div className="mx-auto flex max-w-4xl flex-col gap-16">
          {/* Placeholder content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="rounded-lg border border-dashed border-border bg-muted/20 p-12 text-center"
          >
            <p className="font-mono text-sm text-foreground/60">
              Telemetry data will appear here after analysis completes
            </p>
          </motion.div>
        </div>
      </section>
    )
  }

  return (
    <section className="relative px-6 py-32">
      <SectionHeader
        label="03"
        title="TELEMETRY"
        subtitle="Real-time analysis performance and results visualization"
      />

      <div className="mx-auto flex max-w-6xl flex-col gap-12">
        {/* Progress metrics */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-4">
          <ProgressMetric label="Severity" value={Math.round(severity)} index={0} />
          <ProgressMetric label="Confidence" value={Math.round(confidence)} index={1} />
          <ProgressMetric label="Anomaly Score" value={Math.round(anomalyScore)} index={2} />
          <ProgressMetric label="Signal Quality" value={Math.round(Math.max(0, 100 - differencePercent))} index={3} />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bar Chart - Scores Comparison */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="border border-border rounded-lg bg-card p-6"
          >
            <h3 className="font-mono text-[11px] tracking-[0.2em] text-muted-foreground uppercase mb-4">
              Quality Metrics
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={[
                {
                  name: 'Metrics',
                  'Severity': Math.round(severity),
                  'Confidence': Math.round(confidence),
                  'Quality': Math.round(Math.max(0, 100 - differencePercent)),
                  'Anomaly': Math.min(100, Math.round(anomalyScore))
                }
              ]}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.5)" />
                <YAxis stroke="rgba(255,255,255,0.5)" domain={[0, 100]} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Legend />
                <Bar dataKey="SSIM" fill="#22c55e" radius={[8, 8, 0, 0]} />
                <Bar dataKey="Confidence" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                <Bar dataKey="Signal" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                <Bar dataKey="Severity" fill="#ef4444" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Radar Chart - Metrics Overview */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="border border-border rounded-lg bg-card p-6"
          >
            <h3 className="font-mono text-[11px] tracking-[0.2em] text-muted-foreground uppercase mb-4">
              Analysis Profile
            </h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={[
                { metric: 'SSIM', value: Math.round(ssimPercent), fullMark: 100 },
                { metric: 'Confidence', value: Math.round(confidence), fullMark: 100 },
                { metric: 'Quality', value: Math.round(Math.max(0, 100 - differencePercent)), fullMark: 100 },
                { metric: 'Severity', value: Math.min(100, Math.round(severity)), fullMark: 100 },
                { metric: 'Regions', value: Math.min(100, (analysisResult.regions_detected || 0) * 20), fullMark: 100 }
              ]}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="metric" stroke="rgba(255,255,255,0.5)" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="rgba(255,255,255,0.3)" />
                <Radar name="Score" dataKey="value" stroke="#22c55e" fill="#22c55e" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Detailed Metrics */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <MetricValue label="Severity" value={severity.toFixed(2)} unit="%" index={0} />
          <MetricValue label="Confidence" value={confidence.toFixed(2)} unit="%" index={1} />
          <MetricValue label="SSIM Score" value={ssimScore.toFixed(4)} unit="" index={2} />
          <MetricValue label="Regions" value={analysisResult.regions_detected?.toString() || "0"} unit="found" index={3} />
        </div>

        {/* Summary Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="border-t border-border pt-6 flex flex-wrap items-center justify-between gap-4"
        >
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 flex items-center justify-center rounded-full border border-border bg-green-500/10">
              <span className="text-green-500">✓</span>
            </div>
            <div>
              <span className="font-mono text-[10px] tracking-[0.15em] text-muted-foreground uppercase block">Status</span>
              <span className="font-mono text-xs text-foreground">Analysis Complete</span>
            </div>
          </div>
          <div>
            <span className="font-mono text-[10px] tracking-[0.15em] text-muted-foreground uppercase block">SSIM</span>
            <span className="font-mono text-sm text-foreground font-medium">{ssimScore.toFixed(3)}</span>
          </div>
          <div>
            <span className="font-mono text-[10px] tracking-[0.15em] text-muted-foreground uppercase block">Overall Quality</span>
            <span className="font-mono text-sm text-foreground font-medium">{Math.round((ssimPercent + confidence) / 2)}%</span>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
