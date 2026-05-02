"use client"

import { motion } from "framer-motion"
import { useContext } from "react"
import { SectionHeader } from "./section-header"
import { ResultsDisplay } from "./results-display"
import { AnalysisContext } from "@/app/page"

export function AnalysisSection() {
  const context = useContext(AnalysisContext)
  const analysisResult = context?.analysisResult || null

  return (
    <section className="relative px-6 py-32">
      <SectionHeader
        label="02"
        title="ANALYSIS"
        subtitle={analysisResult ? "Real-time analysis results" : "Upload images to see analysis results"}
      />

      <div className="mx-auto max-w-6xl">
        {analysisResult ? (
          <ResultsDisplay result={analysisResult} />
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="rounded-lg border border-dashed border-border bg-muted/20 p-12 text-center"
          >
            <div className="flex flex-col items-center gap-4">
              <div className="h-12 w-12 rounded-full border border-border/50" />
              <div>
                <p className="font-mono text-sm text-foreground mb-1">
                  Ready for analysis
                </p>
                <p className="font-mono text-xs text-muted-foreground/60">
                  Upload images above to see detailed analysis with heatmaps, regions, and scoring
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </section>
  )
}
