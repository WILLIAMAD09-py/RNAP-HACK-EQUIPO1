import { AnimatePresence, motion } from 'motion/react'

export interface ToastData {
  id: number
  text: string
  tone: 'new' | 'ok' | 'warn'
}

const icons = { new: 'bi-bell-fill', ok: 'bi-check-circle-fill', warn: 'bi-exclamation-triangle-fill' }
const colors = { new: 'bg-coral text-deep', ok: 'bg-[#e3efe7] text-[#3d6b52]', warn: 'bg-doubt text-amber-800' }

export default function Toasts({ toasts }: { toasts: ToastData[] }) {
  return (
    <div className="pointer-events-none fixed right-4 top-20 z-50 flex w-[min(22rem,calc(100vw-2rem))] flex-col gap-2" aria-live="polite">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            layout
            initial={{ opacity: 0, x: 60, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 60 }}
            className="pointer-events-auto flex items-center gap-3 rounded-2xl border border-petrol/10 bg-white p-3 shadow-xl"
          >
            <span className={`grid size-9 shrink-0 place-items-center rounded-xl ${colors[t.tone]}`}>
              <i className={`bi ${icons[t.tone]}`} aria-hidden />
            </span>
            <p className="text-sm font-semibold text-deep">{t.text}</p>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
