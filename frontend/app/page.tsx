"use client"

import { createContext, useState } from "react"
import { StarfieldBackground } from "@/components/starfield-background"
import { HeroSection } from "@/components/hero-section"
import { DataDockingBay } from "@/components/data-docking-bay"
import { AnalysisSection } from "@/components/analysis-section"
import { TelemetryPanel } from "@/components/telemetry-panel"

export const AnalysisContext = createContext<{
  analysisResult: any
  setAnalysisResult: (result: any) => void
} | null>(null)

export default function Home() {
  const [analysisResult, setAnalysisResult] = useState(null)

  return (
    <AnalysisContext.Provider value={{ analysisResult, setAnalysisResult }}>
      <div className="relative min-h-screen bg-background overflow-x-hidden">
        <StarfieldBackground />

        <main className="relative z-10">
          <HeroSection />
          <div className="mx-auto max-w-4xl px-6"><div className="h-px w-full bg-border" /></div>
          <DataDockingBay />
          <div className="mx-auto max-w-4xl px-6"><div className="h-px w-full bg-border" /></div>
          <AnalysisSection />
          <div className="mx-auto max-w-4xl px-6"><div className="h-px w-full bg-border" /></div>
          <TelemetryPanel />

          <footer className="border-t border-border px-6 py-12">
            <div className="mx-auto flex max-w-4xl items-center justify-between">
              <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground/40 uppercase">
                Visual Difference Engine v3.7.2
              </span>
              <span className="font-mono text-[10px] text-muted-foreground/25 tracking-wider uppercase">
                RGB-Thermal Hybrid Protocol
              </span>
            </div>
          </footer>
        </main>
      </div>
    </AnalysisContext.Provider>
  )
}
