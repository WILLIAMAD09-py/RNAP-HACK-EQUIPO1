import { useRef } from 'react'
import { motion, useScroll, useSpring } from 'motion/react'
import SpotlightCard from '../SpotlightCard'
import Reveal, { SectionTitle } from './Reveal'

const steps = [
  { icon: 'bi-mic-fill', title: 'Nota de voz', text: 'El cliente manda su pedido por WhatsApp o Telegram, como siempre lo ha hecho.' },
  { icon: 'bi-soundwave', title: 'Whisper transcribe', text: 'Un modelo de voz convierte el audio en texto, con el español de obra: "cable del doce", "cincuenta metros".' },
  { icon: 'bi-braces-asterisk', title: 'El modelo de lenguaje extrae', text: 'Lee la transcripción y devuelve cliente, producto, cantidad, medida y hora de entrega.' },
  { icon: 'bi-journal-check', title: 'El catálogo empareja', text: 'Con embeddings elige el producto exacto y marca en amarillo lo que una persona debe confirmar.' },
]

export default function HowItWorks() {
  const ref = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start 0.8', 'end 0.6'] })
  const progress = useSpring(scrollYProgress, { stiffness: 90, damping: 24 })

  return (
    <section id="como-funciona" className="bg-mist/60 py-28">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionTitle eyebrow="Cómo funciona" title="Del audio al ticket en cuatro pasos" />
        <div ref={ref} className="relative mt-20">
          <div className="absolute bottom-0 left-7 top-0 w-1 rounded-full bg-petrol/10 lg:left-0 lg:right-0 lg:top-7 lg:h-1 lg:w-auto">
            <motion.div style={{ scaleY: progress }} className="h-full origin-top rounded-full bg-gradient-to-b from-coral to-petrol lg:hidden" />
            <motion.div style={{ scaleX: progress }} className="hidden h-full origin-left rounded-full bg-gradient-to-r from-coral to-petrol lg:block" />
          </div>
          <div className="grid gap-8 ps-20 lg:grid-cols-4 lg:gap-6 lg:ps-0">
            {steps.map((s, i) => (
              <Reveal key={s.title} delay={i * 0.12} className="relative">
                <span className="absolute -left-20 top-0 grid size-14 place-items-center rounded-full bg-petrol text-xl text-white shadow-lg ring-4 ring-mist lg:left-0 lg:z-10">
                  <i className={`bi ${s.icon}`} aria-hidden />
                </span>
                <SpotlightCard theme="light" spotlightColor="#ff7a5c" className="h-full rounded-3xl p-7 lg:mt-16">
                  <p className="text-sm font-bold text-coral">Paso {i + 1}</p>
                  <h3 className="mt-1 text-xl font-extrabold text-deep">{s.title}</h3>
                  <p className="mt-3 leading-relaxed text-petrol/80">{s.text}</p>
                </SpotlightCard>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
