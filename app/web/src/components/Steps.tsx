import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { cn } from '../lib/utils'

const steps = [
  { icon: 'bi-soundwave', label: 'Transcribiendo el audio' },
  { icon: 'bi-braces', label: 'Extrayendo los datos' },
  { icon: 'bi-journal-check', label: 'Buscando en el catálogo' },
]

export default function Steps() {
  const [active, setActive] = useState(0)

  useEffect(() => {
    const a = window.setTimeout(() => setActive(1), 2200)
    const b = window.setTimeout(() => setActive(2), 3800)
    return () => {
      window.clearTimeout(a)
      window.clearTimeout(b)
    }
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="mx-auto w-full max-w-md space-y-3 rounded-3xl bg-white p-6 shadow-xl shadow-deep/10"
      role="status"
      aria-live="polite"
    >
      {steps.map((s, i) => (
        <div key={s.label} className={cn('flex items-center gap-4 rounded-2xl px-4 py-3 transition', i === active ? 'bg-mist' : '')}>
          <span
            className={cn(
              'grid size-10 place-items-center rounded-full text-lg transition',
              i < active ? 'bg-petrol text-white' : i === active ? 'bg-coral text-white' : 'bg-mist text-petrol/50',
            )}
          >
            <i className={cn('bi', i < active ? 'bi-check-lg' : s.icon)} aria-hidden />
          </span>
          <span className={cn('flex-1 font-semibold', i > active ? 'text-ink/40' : 'text-deep')}>{s.label}</span>
          {i === active && <span className="size-4 animate-spin rounded-full border-2 border-coral/30 border-t-coral" />}
        </div>
      ))}
    </motion.div>
  )
}
