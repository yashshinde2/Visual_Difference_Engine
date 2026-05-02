"use client"

import { motion } from "framer-motion"
import { useState, useCallback, useMemo, useEffect, useContext } from "react"
import { Upload, Eye, Thermometer, Check } from "lucide-react"
import { SectionHeader } from "./section-header"
import { ModeSwitch } from "./mode-switch"
import { analyzeImage } from "@/lib/api"
import { AnalysisContext } from "@/app/page"

function UploadPort({
  label,
  icon: Icon,
  accept,
  file,
  onFileChange,
}: {
  label: string
  icon: React.ComponentType<{ className?: string }>
  accept?: string
  file?: File | null
  onFileChange?: (f: File | null) => void
}) {
  const [isDragging, setIsDragging] = useState(false)

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) onFileChange?.(droppedFile)
  }, [onFileChange])

  const handleClick = useCallback(() => {
    const input = document.createElement("input")
    input.type = "file"
    if (accept) input.accept = accept
    input.onchange = (e) => {
      const selectedFile = (e.target as HTMLInputElement).files?.[0]
      if (selectedFile) onFileChange?.(selectedFile)
    }
    input.click()
  }, [accept, onFileChange])

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="flex-1 min-w-[280px]"
    >
      {/* Label */}
      <div className="mb-3 flex items-center gap-3">
        <Icon className="h-3.5 w-3.5 text-muted-foreground" />
        <span className="font-mono text-[11px] tracking-[0.2em] text-muted-foreground uppercase">
          {label}
        </span>
        <div className="flex-1 h-px bg-border" />
        <span className={`font-mono text-[10px] tracking-wider uppercase ${file ? "text-foreground" : "text-muted-foreground/50"}`}>
          {file ? "Ready" : "Empty"}
        </span>
      </div>

      {/* Upload area */}
      <motion.div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        whileHover={{ scale: 1.005 }}
        whileTap={{ scale: 0.995 }}
        transition={{ duration: 0.2 }}
        className={`
          relative cursor-pointer border p-12 transition-colors duration-300
          ${isDragging
            ? "border-foreground/40 bg-foreground/[0.02]"
            : file
              ? "border-foreground/20 bg-foreground/[0.01]"
              : "border-border hover:border-foreground/15"
          }
        `}
      >
        <div className="flex flex-col items-center gap-4">
          {file ? (
            <>
              <div className="flex h-10 w-10 items-center justify-center rounded-full border border-foreground/10">
                <Icon className="h-4 w-4 text-foreground/60" />
              </div>
              <div className="flex flex-col items-center gap-1">
                <span className="font-mono text-xs text-foreground">{file.name}</span>
                <span className="font-mono text-[10px] tracking-wider text-muted-foreground uppercase">
                  Loaded
                </span>
              </div>
            </>
          ) : (
            <>
              <div className={`flex h-10 w-10 items-center justify-center rounded-full border transition-colors duration-300 ${
                isDragging ? "border-foreground/30" : "border-border"
              }`}>
                <Upload className={`h-4 w-4 transition-colors duration-300 ${
                  isDragging ? "text-foreground/60" : "text-muted-foreground"
                }`} />
              </div>
              <div className="flex flex-col items-center gap-1">
                <span className="font-mono text-xs text-foreground/70">
                  {isDragging ? "Release to upload" : "Drop file or click to browse"}
                </span>
                <span className="font-mono text-[10px] text-muted-foreground/50 tracking-wider">
                  PNG, JPG, TIFF, MP4
                </span>
              </div>
            </>
          )}
        </div>
      </motion.div>

    </motion.div>
  )
}

export function DataDockingBay() {
  const context = useContext(AnalysisContext)
  const { setAnalysisResult } = context || {}

  const [mode, setMode] = useState<'image' | 'video'>('image')

  const [rgbBefore, setRgbBefore] = useState<File | null>(null)
  const [rgbAfter, setRgbAfter] = useState<File | null>(null)
  const [thermalBefore, setThermalBefore] = useState<File | null>(null)
  const [thermalAfter, setThermalAfter] = useState<File | null>(null)

  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  // previews
  const rgbBeforeURL = useMemo(() => (rgbBefore ? URL.createObjectURL(rgbBefore) : null), [rgbBefore])
  const rgbAfterURL = useMemo(() => (rgbAfter ? URL.createObjectURL(rgbAfter) : null), [rgbAfter])
  const thermalBeforeURL = useMemo(() => (thermalBefore ? URL.createObjectURL(thermalBefore) : null), [thermalBefore])
  const thermalAfterURL = useMemo(() => (thermalAfter ? URL.createObjectURL(thermalAfter) : null), [thermalAfter])

  useEffect(() => {
    return () => {
      if (rgbBeforeURL) URL.revokeObjectURL(rgbBeforeURL)
      if (rgbAfterURL) URL.revokeObjectURL(rgbAfterURL)
      if (thermalBeforeURL) URL.revokeObjectURL(thermalBeforeURL)
      if (thermalAfterURL) URL.revokeObjectURL(thermalAfterURL)
    }
  }, [rgbBeforeURL, rgbAfterURL, thermalBeforeURL, thermalAfterURL])

  async function handleAnalyze() {
    setError(null)
    setProgress(0)

    if (!rgbBefore || !rgbAfter) return setError('Attach both RGB before and after files')

    const form = new FormData()
    form.append('rgb_before', rgbBefore)
    form.append('rgb_after', rgbAfter)
    if (thermalBefore) form.append('thermal_before', thermalBefore)
    if (thermalAfter) form.append('thermal_after', thermalAfter)

    try {
      setLoading(true)
      const res = await analyzeImage(form, { onProgress: (p) => setProgress(p), mode })
      setAnalysisResult?.(res)
    } catch (e: any) {
      setError(e?.message || String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="relative px-6 py-32">
      <SectionHeader
        label="01"
        title="DATA INPUT"
        subtitle="Upload RGB and thermal image data for multi-modal analysis"
      />

      <div className="mx-auto flex max-w-lg justify-center mb-6">
        <ModeSwitch mode={mode} onChange={(m) => setMode(m)} />
      </div>

      <div className="mx-auto flex max-w-4xl flex-col items-stretch gap-6">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <h4 className="font-mono text-xs text-muted-foreground mb-3">RGB — Before</h4>
            <div className="flex flex-col gap-3">
              <UploadPort accept={mode === 'image' ? 'image/*' : 'video/*'} file={rgbBefore} onFileChange={setRgbBefore} label="RGB Before" icon={Eye} />
              {rgbBeforeURL && mode === 'image' && (
                <div className="relative w-full aspect-square bg-muted rounded-lg border border-border overflow-hidden flex items-center justify-center">
                  <img src={rgbBeforeURL} className="w-full h-full object-contain p-2" alt="rgb before" />
                </div>
              )}
              {rgbBeforeURL && mode === 'video' && (
                <div className="relative w-full aspect-video bg-muted rounded-lg border border-border overflow-hidden">
                  <video src={rgbBeforeURL} className="w-full h-full object-contain" controls />
                </div>
              )}
            </div>
          </div>

          <div>
            <h4 className="font-mono text-xs text-muted-foreground mb-3">RGB — After</h4>
            <div className="flex flex-col gap-3">
              <UploadPort accept={mode === 'image' ? 'image/*' : 'video/*'} file={rgbAfter} onFileChange={setRgbAfter} label="RGB After" icon={Eye} />
              {rgbAfterURL && mode === 'image' && (
                <div className="relative w-full aspect-square bg-muted rounded-lg border border-border overflow-hidden flex items-center justify-center">
                  <img src={rgbAfterURL} className="w-full h-full object-contain p-2" alt="rgb after" />
                </div>
              )}
              {rgbAfterURL && mode === 'video' && (
                <div className="relative w-full aspect-video bg-muted rounded-lg border border-border overflow-hidden">
                  <video src={rgbAfterURL} className="w-full h-full object-contain" controls />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div>
            <h4 className="font-mono text-xs text-muted-foreground mb-3">Thermal — Before (optional)</h4>
            <div className="flex flex-col gap-3">
              <UploadPort accept={mode === 'image' ? 'image/*' : 'video/*'} file={thermalBefore} onFileChange={setThermalBefore} label="Thermal Before" icon={Thermometer} />
              {thermalBeforeURL && mode === 'image' && (
                <div className="relative w-full aspect-square bg-muted rounded-lg border border-border overflow-hidden flex items-center justify-center">
                  <img src={thermalBeforeURL} className="w-full h-full object-contain p-2" alt="thermal before" />
                </div>
              )}
              {thermalBeforeURL && mode === 'video' && (
                <div className="relative w-full aspect-video bg-muted rounded-lg border border-border overflow-hidden">
                  <video src={thermalBeforeURL} className="w-full h-full object-contain" controls />
                </div>
              )}
            </div>
          </div>

          <div>
            <h4 className="font-mono text-xs text-muted-foreground mb-3">Thermal — After (optional)</h4>
            <div className="flex flex-col gap-3">
              <UploadPort accept={mode === 'image' ? 'image/*' : 'video/*'} file={thermalAfter} onFileChange={setThermalAfter} label="Thermal After" icon={Thermometer} />
              {thermalAfterURL && mode === 'image' && (
                <div className="relative w-full aspect-square bg-muted rounded-lg border border-border overflow-hidden flex items-center justify-center">
                  <img src={thermalAfterURL} className="w-full h-full object-contain p-2" alt="thermal after" />
                </div>
              )}
              {thermalAfterURL && mode === 'video' && (
                <div className="relative w-full aspect-video bg-muted rounded-lg border border-border overflow-hidden">
                  <video src={thermalAfterURL} className="w-full h-full object-contain" controls />
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="mt-8">
          <motion.button
            onClick={handleAnalyze}
            disabled={loading || !rgbBefore || !rgbAfter}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="relative inline-flex items-center gap-2 rounded-lg border border-foreground/20 bg-foreground/5 px-6 py-3 text-sm font-medium transition-all duration-300 hover:border-foreground/40 hover:bg-foreground/10 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="h-4 w-4 rounded-full border-2 border-foreground/30 border-t-foreground/60"
                />
                <span>Analyzing… {progress}%</span>
              </>
            ) : (
              <>
                <Check className="h-4 w-4" />
                <span>Analyze Images</span>
              </>
            )}
          </motion.button>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 rounded-lg border border-destructive/30 bg-destructive/5 p-4"
            >
              <p className="font-mono text-sm text-destructive">{error}</p>
            </motion.div>
          )}
        </div>
      </div>
    </section>
  )
}
