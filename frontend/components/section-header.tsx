"use client"

import { motion } from "framer-motion"

export function SectionHeader({
  label,
  title,
  subtitle,
}: {
  label: string
  title: string
  subtitle?: string
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6 }}
      className="mb-16 flex flex-col items-center gap-4"
    >
      <span className="font-mono text-[11px] tracking-[0.3em] text-muted-foreground uppercase">
        {label}
      </span>
      <h2 className="text-center text-2xl font-light tracking-[0.12em] text-foreground sm:text-3xl text-balance">
        {title}
      </h2>
      {subtitle && (
        <p className="max-w-md text-center font-mono text-[11px] leading-relaxed text-muted-foreground tracking-wide text-pretty">
          {subtitle}
        </p>
      )}
    </motion.div>
  )
}
