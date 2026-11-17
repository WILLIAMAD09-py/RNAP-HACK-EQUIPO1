import type { ReactNode } from 'react'
import { motion } from 'motion/react'

export default function Reveal({ children, delay = 0, className, x = 0 }: { children: ReactNode; delay?: number; className?: string; x?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 40, x }}
      whileInView={{ opacity: 1, y: 0, x: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.8, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

export function SectionTitle({ eyebrow, title, light = false }: { eyebrow: string; title: string; light?: boolean }) {
  return (
    <Reveal className="mx-auto max-w-3xl text-center">
      <p className={`text-sm font-bold uppercase tracking-[0.25em] ${light ? 'text-coral-soft' : 'text-coral'}`}>{eyebrow}</p>
      <h2 className={`mt-3 text-4xl font-extrabold leading-tight tracking-tight sm:text-6xl ${light ? 'text-white' : 'text-deep'}`}>{title}</h2>
    </Reveal>
  )
}
