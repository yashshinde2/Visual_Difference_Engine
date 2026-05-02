"use client"

import { motion } from "framer-motion"
import { useState } from "react"
import { ChevronDown, ImageIcon, Zap } from "lucide-react"
import { getImageUrl } from "@/lib/api"

interface AnalysisResult {
  analysis_id: string
  mode: "rgb" | "hybrid"
  metrics: {
    ssim_score: number
    ssim_percent: number
    mse: number
    mean_error: number
    psnr: number
    difference_percentage: number
    changed_pixels: number
    anomaly_score: number
    severity: number
    confidence: number
    integrity: number
    histogram_similarity: number
    edge_difference: number
    region_count: number
    region_density: number
    mask_coverage: number
    thermal_variation: number
  }
  regions_detected: number
  output: {
    overlay_image: string
    heatmap_image: string
    regions: string[]
  }
}

export function ResultsDisplay({ result }: { result: AnalysisResult | null }) {
  const [expandedRegion, setExpandedRegion] = useState<number | null>(null)

  if (!result) return null

  const scores = result.metrics || {}

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="mx-auto max-w-6xl"
    >
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <span className="font-mono text-[11px] tracking-[0.2em] text-muted-foreground uppercase">
              Analysis ID
            </span>
            <p className="font-mono text-xs text-foreground mt-1">{result.analysis_id}</p>
          </div>
          <div>
            <span className="font-mono text-[11px] tracking-[0.2em] text-muted-foreground uppercase">
              Mode
            </span>
            <p className="font-mono text-xs text-foreground mt-1 uppercase">
              {result.mode} Analysis
            </p>
          </div>
        </div>
      </div>

      {/* Main Analysis Visualization */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Overlay Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="border border-border rounded-lg overflow-hidden bg-card p-4"
        >
          <div className="mb-3 flex items-center gap-2">
            <ImageIcon className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground uppercase">
              Overlay Detection
            </span>
          </div>
          {result.output.overlay_image && (
            <div className="relative w-full aspect-video bg-muted rounded overflow-hidden">
              <img
                src={getImageUrl(result.output.overlay_image)}
                alt="Overlay analysis"
                className="w-full h-full object-contain"
                onError={(e) => {
                  console.error("Failed to load overlay image:", result.output.overlay_image);
                  (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23f0f0f0" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" font-family="monospace" font-size="12" fill="%23999"%3EImage Error%3C/text%3E%3C/svg%3E'
                }}
              />
            </div>
          )}
        </motion.div>

        {/* Heatmap Image */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="border border-border rounded-lg overflow-hidden bg-card p-4"
        >
          <div className="mb-3 flex items-center gap-2">
            <Zap className="h-3.5 w-3.5 text-muted-foreground" />
            <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground uppercase">
              Heatmap Intensity
            </span>
          </div>
          {result.output.heatmap_image && (
            <div className="relative w-full aspect-video bg-muted rounded overflow-hidden">
              <img
                src={getImageUrl(result.output.heatmap_image)}
                alt="Heatmap analysis"
                className="w-full h-full object-contain"
                onError={(e) => {
                  console.error("Failed to load heatmap image:", result.output.heatmap_image);
                  (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23f0f0f0" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" font-family="monospace" font-size="12" fill="%23999"%3EImage Error%3C/text%3E%3C/svg%3E'
                }}
              />
            </div>
          )}
        </motion.div>
      </div>

      {/* Scores Grid */}
      <div className="mb-8 grid grid-cols-2 md:grid-cols-3 gap-4">
        <ScoreCard
          label="Severity"
          value={scores.severity?.toFixed(2) || "N/A"}
          unit="%"
          delay={0.1}
        />
        <ScoreCard
          label="Confidence"
          value={scores.confidence?.toFixed(2) || "N/A"}
          unit="%"
          delay={0.15}
        />
        <ScoreCard
          label="SSIM Score"
          value={scores.ssim_score?.toFixed(4) || "N/A"}
          unit=""
          delay={0.2}
        />
        <ScoreCard
          label="Integrity"
          value={scores.integrity?.toFixed(2) || "N/A"}
          unit="%"
          delay={0.25}
        />
        <ScoreCard
          label="Anomaly Score"
          value={scores.anomaly_score?.toFixed(2) || "N/A"}
          unit="%"
          delay={0.3}
        />
        <ScoreCard
          label="Regions Detected"
          value={result.regions_detected?.toString() || "0"}
          unit="areas"
          delay={0.35}
        />
      </div>

      {/* Regions of Interest */}
      {result.output.regions && result.output.regions.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.5 }}
          className="border border-border rounded-lg bg-card p-6"
        >
          <div className="mb-4">
            <span className="font-mono text-[11px] tracking-[0.2em] text-muted-foreground uppercase">
              Regions of Interest ({result.output.regions.length})
            </span>
          </div>

          <div className="space-y-3">
            {result.output.regions.map((region, idx) => (
              <RegionItem
                key={idx}
                index={idx}
                region={region}
                isExpanded={expandedRegion === idx}
                onToggle={() =>
                  setExpandedRegion(expandedRegion === idx ? null : idx)
                }
              />
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

function ScoreCard({
  label,
  value,
  unit,
  delay,
}: {
  label: string
  value: string
  unit: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="border border-border rounded-lg bg-card p-4"
    >
      <span className="font-mono text-[9px] tracking-[0.15em] text-muted-foreground uppercase block mb-2">
        {label}
      </span>
      <div className="flex items-baseline gap-1">
        <span className="font-mono text-xl font-light text-foreground">{value}</span>
        {unit && (
          <span className="font-mono text-[10px] text-muted-foreground/70">
            {unit}
          </span>
        )}
      </div>
    </motion.div>
  )
}

function RegionItem({
  index,
  region,
  isExpanded,
  onToggle,
}: {
  index: number
  region: string
  isExpanded: boolean
  onToggle: () => void
}) {
  return (
    <motion.div
      className="border border-border rounded-lg overflow-hidden bg-muted/30 hover:bg-muted/50 transition-colors"
    >
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-foreground/5 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded border border-border bg-card">
            <span className="font-mono text-[10px] font-medium">{index + 1}</span>
          </div>
          <div className="text-left">
            <span className="font-mono text-xs text-foreground block">
              Region {index + 1}
            </span>
            <span className="font-mono text-[9px] text-muted-foreground/60">
              {region.split("/").pop()}
            </span>
          </div>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </motion.div>
      </button>

      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.3 }}
          className="border-t border-border bg-card p-4"
        >
          <img
            src={getImageUrl(region)}
            alt={`Region ${index + 1}`}
            className="w-full rounded-lg border border-border/50 max-h-64 object-contain"
            onError={(e) => {
              console.error("Failed to load region image:", region);
              (e.target as HTMLImageElement).src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23f0f0f0" width="100" height="100"/%3E%3Ctext x="50" y="50" text-anchor="middle" dy=".3em" font-family="monospace" font-size="12" fill="%23999"%3EImage Error%3C/text%3E%3C/svg%3E'
            }}
          />
          <span className="font-mono text-[9px] text-muted-foreground/50 mt-2 block">
            {region}
          </span>
        </motion.div>
      )}
    </motion.div>
  )
}
