import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'motion/react'
import Reveal, { SectionTitle } from './Reveal'

export default function BeforeAfter() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start 0.85', 'center 0.5'] })
  const reveal = useTransform(scrollYProgress, [0, 1], [0, 100])
  const clip = useTransform(reveal, (v) => `inset(0 ${100 - v}% 0 0)`)
  const lineLeft = useTransform(reveal, (v) => `${v}%`)

  return (
    <section id="problema" className="mx-auto max-w-6xl px-4 py-28 sm:px-6">
      <SectionTitle eyebrow="El problema" title="Una medida mal escuchada es una entrega perdida" />
      <Reveal className="mx-auto mt-6 max-w-2xl text-center text-lg text-petrol/80">
        Con prisa, los números se cruzan. Desliza para ver el mismo pedido capturado a mano y con Receipt.
      </Reveal>
      <div ref={ref} className="relative mx-auto mt-14 max-w-4xl">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-3xl bg-[#fffdf5] p-8 shadow-xl shadow-deep/10 ring-1 ring-black/5 [background-image:repeating-linear-gradient(transparent,transparent_31px,#cfd8dc_32px)]">
            <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-petrol/60">
              <i className="bi bi-pencil-fill" aria-hidden /> A mano
            </p>
            <p className="mt-5 font-serif text-3xl italic text-ink/80 sm:text-4xl">Pedro</p>
            <p className="relative mt-2 inline-block font-serif text-3xl italic text-ink/80 sm:text-4xl">
              50 m cable cal. 10
              <motion.span
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5, duration: 0.7 }}
                className="absolute inset-x-0 top-1/2 h-1 origin-left -rotate-2 rounded bg-coral"
              />
            </p>
            <p className="mt-4 flex items-center gap-2 text-sm font-bold text-coral">
              <i className="bi bi-x-circle-fill" aria-hidden /> El cliente pidió calibre 12
            </p>
          </div>

          <div className="relative min-h-52">
            <div className="absolute inset-0 grid place-items-center rounded-3xl bg-white/50 ring-1 ring-black/5">
              <i className="bi bi-receipt text-4xl text-petrol/25" aria-hidden />
            </div>
            <motion.div style={{ clipPath: clip }} className="absolute inset-0 rounded-3xl bg-white p-8 shadow-xl shadow-deep/10 ring-2 ring-petrol/15">
              <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-petrol/60">
                <i className="bi bi-receipt-cutoff text-coral" aria-hidden /> Receipt
              </p>
              <p className="mt-5 text-3xl font-extrabold text-deep sm:text-4xl">Pedro</p>
              <p className="mt-2 text-3xl font-extrabold text-deep sm:text-4xl">
                50 m cable <mark className="rounded bg-coral/30 px-1 text-deep">cal. 12</mark>
              </p>
              <p className="mt-4 flex items-center gap-2 text-sm font-bold text-emerald-700">
                <i className="bi bi-check-circle-fill" aria-hidden /> Coincide con la nota de voz
              </p>
            </motion.div>
            <motion.div style={{ left: lineLeft }} className="pointer-events-none absolute inset-y-0 z-10 w-0.5 bg-coral shadow-[0_0_16px_rgba(255,122,92,0.7)]" />
          </div>
        </div>
      </div>
    </section>
  )
}
