import { useEffect, useState } from 'react'
import { AnimatePresence, motion, useReducedMotion } from 'motion/react'

const fields = [
  { label: 'Cliente', value: 'Pedro', icon: 'bi-person-fill', highlight: false },
  { label: 'Producto', value: 'Cable THW calibre 12', icon: 'bi-box-seam-fill', highlight: true },
  { label: 'Cantidad', value: '50 m', icon: 'bi-rulers', highlight: false },
  { label: 'Entrega', value: '15:00', icon: 'bi-clock-fill', highlight: false },
]

const bars = Array.from({ length: 28 }, (_, i) => 0.25 + 0.75 * Math.abs(Math.sin(i * 1.7) * Math.cos(i * 0.6)))

type Phase = 'idle' | 'voice' | 'transcribing' | 'ticket'

function VoiceBubble({ playing }: { playing: boolean }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.9 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className="flex w-[88%] items-center gap-3 rounded-2xl rounded-tl-md bg-white p-3 shadow-md"
    >
      <span className="grid size-9 shrink-0 place-items-center rounded-full bg-petrol text-white">
        <i className={`bi ${playing ? 'bi-pause-fill' : 'bi-play-fill'}`} aria-hidden />
      </span>
      <div className="flex h-8 flex-1 items-center gap-[2px]">
        {bars.map((h, i) => (
          <motion.span
            key={i}
            className="w-[3px] rounded-full bg-petrol/70"
            style={{ height: `${h * 100}%` }}
            animate={playing ? { scaleY: [1, 0.35, 1.1, 0.6, 1] } : { scaleY: 1 }}
            transition={playing ? { duration: 0.9, repeat: Infinity, delay: i * 0.03 } : { duration: 0.2 }}
          />
        ))}
      </div>
      <span className="text-[11px] font-semibold text-petrol/60">0:07</span>
    </motion.div>
  )
}

export default function PhoneDemo() {
  const reduced = useReducedMotion()
  const [phase, setPhase] = useState<Phase>(reduced ? 'ticket' : 'idle')
  const [filled, setFilled] = useState(reduced ? fields.length : 0)

  useEffect(() => {
    if (reduced) return
    const timers: number[] = []
    const at = (ms: number, fn: () => void) => timers.push(window.setTimeout(fn, ms))
    const run = () => {
      setPhase('idle')
      setFilled(0)
      at(600, () => setPhase('voice'))
      at(3400, () => setPhase('transcribing'))
      at(5000, () => setPhase('ticket'))
      fields.forEach((_, i) => at(5600 + i * 750, () => setFilled(i + 1)))
      at(10800, run)
    }
    run()
    return () => timers.forEach(window.clearTimeout)
  }, [reduced])

  const showVoice = phase !== 'idle'
  const showTicket = phase === 'ticket'

  return (
    <motion.div
      animate={reduced ? undefined : { y: [0, -12, 0], rotate: [-1, 1, -1] }}
      transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
      className="relative mx-auto w-[280px] sm:w-[310px]"
    >
      <div className="absolute -inset-8 -z-10 rounded-full bg-coral/25 blur-3xl" />
      <div className="rounded-[44px] bg-ink p-2.5 shadow-2xl shadow-black/50 ring-1 ring-white/20">
        <div className="relative h-[560px] overflow-hidden rounded-[36px] bg-[#e9e4da]">
          <div className="absolute left-1/2 top-2 z-20 h-5 w-24 -translate-x-1/2 rounded-full bg-ink" />
          <div className="flex items-center gap-3 bg-petrol px-4 pb-3 pt-9 text-white">
            <span className="grid size-9 place-items-center rounded-full bg-coral font-extrabold text-deep">P</span>
            <div>
              <p className="text-sm font-bold leading-tight">Pedro</p>
              <p className="text-[11px] text-white/70">en línea</p>
            </div>
            <i className="bi bi-whatsapp ms-auto text-lg text-coral-soft" aria-hidden />
          </div>
          <div className="flex flex-col gap-3 p-3">
            {showVoice && <VoiceBubble playing={phase === 'voice'} />}
            <AnimatePresence>
              {phase === 'transcribing' && (
                <motion.div
                  key="tr"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="flex w-fit items-center gap-2 self-end rounded-2xl rounded-tr-md bg-white/80 px-3 py-2 text-xs font-semibold text-petrol shadow"
                >
                  <i className="bi bi-soundwave text-coral" aria-hidden />
                  transcribiendo
                  <span className="flex gap-0.5">
                    {[0, 1, 2].map((d) => (
                      <motion.span
                        key={d}
                        className="size-1 rounded-full bg-petrol"
                        animate={{ opacity: [0.2, 1, 0.2] }}
                        transition={{ duration: 1, repeat: Infinity, delay: d * 0.2 }}
                      />
                    ))}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
            <AnimatePresence>
              {showTicket && (
                <motion.div
                  key="ticket"
                  initial={{ opacity: 0, y: 40, scale: 0.92 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ type: 'spring', stiffness: 140, damping: 16 }}
                  className="receipt-paper rounded-t-2xl bg-white px-4 pb-6 pt-4 shadow-xl"
                >
                  <div className="flex items-center justify-between border-b border-dashed border-petrol/25 pb-2">
                    <p className="flex items-center gap-1.5 text-sm font-extrabold text-deep">
                      <i className="bi bi-receipt text-coral" aria-hidden /> Ticket
                    </p>
                    <p className="text-[10px] font-semibold text-petrol/60">Los Nogales</p>
                  </div>
                  <ul className="mt-3 space-y-2.5">
                    {fields.map((f, i) => (
                      <li key={f.label} className="min-h-[46px]">
                        {filled > i && (
                          <motion.div
                            initial={{ opacity: 0, x: -14 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.45 }}
                            className={`rounded-xl px-3 py-2 ${f.highlight ? 'bg-doubt ring-2 ring-doubt-border' : 'bg-mist/70'}`}
                          >
                            <p className="flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider text-petrol/60">
                              <i className={`bi ${f.icon}`} aria-hidden /> {f.label}
                            </p>
                            <p className="text-sm font-extrabold text-deep">
                              {f.highlight ? (
                                <>
                                  Cable THW{' '}
                                  <motion.mark
                                    initial={{ backgroundSize: '0% 100%' }}
                                    animate={{ backgroundSize: '100% 100%' }}
                                    transition={{ delay: 0.4, duration: 0.6 }}
                                    className="rounded bg-gradient-to-r from-coral/40 to-coral/40 bg-no-repeat px-1 text-deep"
                                  >
                                    calibre 12
                                  </motion.mark>
                                </>
                              ) : (
                                f.value
                              )}
                            </p>
                          </motion.div>
                        )}
                      </li>
                    ))}
                  </ul>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
