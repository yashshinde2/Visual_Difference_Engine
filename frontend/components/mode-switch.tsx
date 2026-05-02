"use client"

import { motion } from "framer-motion"
import { useState } from "react"
import { Camera, Film } from "lucide-react"

type Mode = "image" | "video"

export function ModeSwitch({ mode, onChange }: { mode?: Mode; onChange?: (m: Mode) => void }) {
  const [internalMode, setInternalMode] = useState<Mode>(mode ?? "image")

  // keep controlled/uncontrolled in sync
  const activeMode = mode ?? internalMode

  function setMode(m: Mode) {
    setInternalMode(m)
    onChange?.(m)
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="flex flex-col items-center gap-3"
    >
      <div className="relative flex items-center rounded border border-border bg-card p-0.5">
        {/* Sliding indicator */}
        <motion.div
          className="absolute top-0.5 bottom-0.5 rounded-sm bg-foreground/5"
          animate={{
            left: activeMode === "image" ? "2px" : "50%",
            width: "calc(50% - 2px)",
          }}
          transition={{ type: "spring", stiffness: 400, damping: 35 }}
        />

        <button
          onClick={() => setMode("image")}
          className={`relative z-10 flex items-center gap-2.5 px-6 py-2.5 font-mono text-[11px] tracking-[0.15em] uppercase transition-colors duration-300 ${
            activeMode === "image" ? "text-foreground" : "text-muted-foreground hover:text-foreground/70"
          }`}
        >
          <Camera className="h-3.5 w-3.5" />
          <span>Image</span>
        </button>

        <button
          onClick={() => setMode("video")}
          className={`relative z-10 flex items-center gap-2.5 px-6 py-2.5 font-mono text-[11px] tracking-[0.15em] uppercase transition-colors duration-300 ${
            activeMode === "video" ? "text-foreground" : "text-muted-foreground hover:text-foreground/70"
          }`}
        >
          <Film className="h-3.5 w-3.5" />
          <span>Video</span>
        </button>
      </div>
    </motion.div>
  )
}
