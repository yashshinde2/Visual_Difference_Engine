"use client"

import { motion } from "framer-motion"

export function HeroSection() {
  return (
    <section className="relative flex min-h-screen flex-col items-center justify-center px-6">
      <div className="flex flex-col items-center gap-8">
        {/* Status line */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 1 }}
          className="flex items-center gap-3"
        >
          <div className="h-1.5 w-1.5 rounded-full bg-foreground/40" />
          <span className="font-mono text-[11px] tracking-[0.25em] text-muted-foreground uppercase">
            System Active
          </span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.8 }}
          className="text-center text-5xl font-light tracking-[0.15em] text-foreground sm:text-6xl md:text-7xl lg:text-8xl text-balance"
        >
          MISSION ANALYSIS
        </motion.h1>

        {/* Divider */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
          className="h-px w-48 bg-foreground/20"
        />

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.8 }}
          className="font-mono text-xs tracking-[0.3em] text-muted-foreground uppercase"
        >
          Multi-Modal Visual Difference Engine
        </motion.p>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2.5, duration: 1 }}
          className="mt-24 flex flex-col items-center gap-3"
        >
          <span className="font-mono text-[10px] tracking-[0.2em] text-muted-foreground/50 uppercase">
            Scroll
          </span>
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="h-6 w-px bg-foreground/15"
          />
        </motion.div>
      </div>
    </section>
  )
}
