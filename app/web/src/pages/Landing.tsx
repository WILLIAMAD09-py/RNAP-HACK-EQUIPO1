import { useEffect, useRef, useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { motion, useMotionValue, useSpring } from 'motion/react'
import Aurora from '../components/Aurora'
import SplitText from '../components/SplitText'
import StarBorder from '../components/StarBorder'
import SpotlightCard from '../components/SpotlightCard'
import CountUp from '../components/CountUp'
import { api, type Metric } from '../api'

function Reveal({ children, delay = 0, className }: { children: ReactNode; delay?: number; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 36 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.7, delay, ease: 'easeOut' }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

function MagneticCta() {
  const ref = useRef<HTMLDivElement>(null)
  const x = useSpring(useMotionValue(0), { stiffness: 200, damping: 15 })
  const y = useSpring(useMotionValue(0), { stiffness: 200, damping: 15 })

  const move = (e: React.MouseEvent) => {
    const r = ref.current!.getBoundingClientRect()
    x.set((e.clientX - (r.left + r.width / 2)) * 0.25)
    y.set((e.clientY - (r.top + r.height / 2)) * 0.35)
  }
  const leave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <div ref={ref} onMouseMove={move} onMouseLeave={leave} className="inline-block p-6">
      <motion.div style={{ x, y }}>
        <StarBorder
          as={Link}
          to="/app"
          color="#ff7a5c"
          trailColor="#ffb4a2"
          radius={44}
          thickness={3}
          backgroundColor="#0e4a5a"
          textColor="#ffffff"
          theme="dark"
          className="shadow-[0_20px_60px_-10px_rgba(255,122,92,0.55)]"
        >
          <span className="flex items-center gap-4 px-8 py-5 text-2xl font-extrabold sm:px-14 sm:py-7 sm:text-4xl">
            <i className="bi bi-mic-fill" aria-hidden />
            Probar Receipt
            <i className="bi bi-arrow-right" aria-hidden />
          </span>
        </StarBorder>
      </motion.div>
    </div>
  )
}

const steps = [
  {
    icon: 'bi-soundwave',
    title: 'Whisper transcribe',
    text: 'Un modelo de reconocimiento de voz convierte la nota de WhatsApp en texto, con el español de obra: "cable del doce", "cincuenta metros".',
  },
  {
    icon: 'bi-braces-asterisk',
    title: 'Un modelo de lenguaje extrae',
    text: 'Lee la transcripción y devuelve los cinco campos del pedido: cliente, producto, cantidad, medida y hora de entrega.',
  },
  {
    icon: 'bi-journal-check',
    title: 'El catálogo confirma',
    text: 'Con embeddings empareja lo dicho con uno de los 42 productos y marca en amarillo lo que debe revisar una persona.',
  },
]

const testRuns = [
  { name: 'baseline_test', label: 'Línea base: Whisper small + reglas' },
  { name: 'pretrained_test', label: 'Preentrenado: Whisper medium + LLM' },
  { name: 'solution_test', label: 'Receipt: solución híbrida' },
]

const team = ['William', 'Jack', 'Carlos', 'Jesús']

function Results() {
  const [metrics, setMetrics] = useState<Metric[] | null>(null)

  useEffect(() => {
    api.metrics().then(setMetrics).catch(() => setMetrics([]))
  }, [])

  if (metrics === null) {
    return <div className="mx-auto h-40 max-w-md animate-pulse rounded-3xl bg-mist" />
  }
  const shown = testRuns
    .map((r) => ({ metric: metrics.find((m) => m.name === r.name && m.split === 'test'), label: r.label }))
    .filter((r): r is { metric: Metric; label: string } => r.metric !== undefined)
  if (shown.length === 0) {
    return (
      <div className="mx-auto max-w-md rounded-3xl border-2 border-dashed border-petrol/20 bg-white p-10 text-center">
        <i className="bi bi-hourglass-split text-3xl text-coral" aria-hidden />
        <p className="mt-3 text-xl font-bold text-deep">Resultados en evaluación</p>
        <p className="mt-1 text-sm text-petrol/70">Publicaremos las cifras reales cuando terminen las corridas.</p>
      </div>
    )
  }
  return (
    <div>
      <div className="grid gap-6 md:grid-cols-3">
        {shown.map(({ metric: m, label }) => {
          const hero = m.name === 'solution_test'
          return (
            <Reveal key={m.name}>
              <div className={`h-full rounded-3xl p-7 shadow-xl ${hero ? 'bg-coral/10 ring-2 ring-coral shadow-coral/20' : 'bg-white shadow-deep/5'}`}>
                <h3 className={`text-lg font-extrabold ${hero ? 'text-coral' : 'text-deep'}`}>{label}</h3>
                <div className="mt-6 grid grid-cols-3 gap-3 text-center">
                  <div>
                    <p className={`text-3xl font-extrabold ${hero ? 'text-coral' : 'text-petrol'}`}>
                      <CountUp to={m.fields_correct * 100} decimals={0} suffix="%" />
                    </p>
                    <p className="mt-1 text-xs font-semibold text-petrol/70">Campos correctos</p>
                  </div>
                  <div>
                    <p className={`text-3xl font-extrabold ${hero ? 'text-coral' : 'text-petrol'}`}>
                      <CountUp to={m.wer * 100} decimals={1} suffix="%" />
                    </p>
                    <p className="mt-1 text-xs font-semibold text-petrol/70">WER</p>
                  </div>
                  <div>
                    <p className={`text-3xl font-extrabold ${hero ? 'text-coral' : 'text-petrol'}`}>
                      <CountUp to={m.total_seconds_mean} decimals={1} suffix=" s" />
                    </p>
                    <p className="mt-1 text-xs font-semibold text-petrol/70">Tiempo medio</p>
                  </div>
                </div>
              </div>
            </Reveal>
          )
        })}
      </div>
      <p className="mt-6 text-center text-sm text-petrol/70">
        Conjunto de prueba: {shown[0].metric.notes} notas de voz grabadas por el equipo
      </p>
    </div>
  )
}

export default function Landing() {
  return (
    <div className="bg-cream">
      <section className="relative isolate flex min-h-screen flex-col overflow-hidden bg-deep text-white">
        <div className="absolute inset-0 -z-10 opacity-80">
          <Aurora colorStops={['#0e4a5a', '#ff7a5c', '#1b7a8c']} amplitude={0.9} blend={0.6} speed={0.5} />
        </div>
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-deep/30 via-transparent to-deep" />

        <nav className="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-6">
          <span className="flex items-center gap-2.5 text-lg font-extrabold">
            <span className="grid size-9 place-items-center rounded-xl bg-coral text-deep">
              <i className="bi bi-receipt-cutoff" aria-hidden />
            </span>
            Receipt
          </span>
          <span className="hidden text-sm font-semibold text-white/70 sm:block">Ferretería Los Nogales · Monterrey</span>
        </nav>

        <div className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-5 pb-16 text-center">
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-semibold backdrop-blur"
          >
            <i className="bi bi-whatsapp text-coral-soft" aria-hidden /> Del audio de WhatsApp al ticket
          </motion.p>
          <SplitText
            text="De nota de voz a pedido en segundos"
            tag="h1"
            splitType="words"
            trigger="load"
            textAlign="center"
            className="text-4xl font-extrabold leading-tight text-white sm:text-6xl lg:text-7xl"
          />
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.1 }}
            className="mt-6 max-w-2xl text-lg text-white/75 sm:text-xl"
          >
            Graba o sube la nota del cliente. Receipt escribe el ticket y te avisa qué dato conviene confirmar antes de salir a entregar.
          </motion.p>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 1.4, type: 'spring' }} className="mt-10">
            <MagneticCta />
          </motion.div>
        </div>
        <motion.a
          href="#problema"
          animate={{ y: [0, 8, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="mx-auto mb-6 text-2xl text-white/60"
          aria-label="Ir a la siguiente sección"
        >
          <i className="bi bi-chevron-double-down" aria-hidden />
        </motion.a>
      </section>

      <section id="problema" className="mx-auto max-w-6xl px-5 py-24">
        <Reveal className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-bold uppercase tracking-[0.25em] text-coral">El problema</p>
          <h2 className="mt-3 text-3xl font-extrabold text-deep sm:text-5xl">Una medida mal escuchada es una entrega perdida</h2>
          <p className="mt-5 text-lg text-petrol/80">
            Los clientes de Ferretería Los Nogales piden por notas de voz y el personal las captura a mano. Con prisa, los números se cruzan.
          </p>
        </Reveal>
        <div className="mt-14 grid items-stretch gap-6 md:grid-cols-[1fr_auto_1fr]">
          <Reveal>
            <div className="h-full rounded-3xl bg-white p-8 shadow-xl shadow-deep/5">
              <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-petrol/70">
                <i className="bi bi-mic" aria-hidden /> El cliente pidió
              </p>
              <p className="mt-4 text-3xl font-extrabold text-deep">Cable del 12</p>
              <p className="mt-1 text-lg text-petrol/70">50 metros</p>
            </div>
          </Reveal>
          <Reveal delay={0.15} className="grid place-items-center text-3xl text-coral">
            <i className="bi bi-arrow-right-circle-fill hidden md:block" aria-hidden />
            <i className="bi bi-arrow-down-circle-fill md:hidden" aria-hidden />
          </Reveal>
          <Reveal delay={0.3}>
            <div className="h-full rounded-3xl border-2 border-doubt-border bg-doubt p-8 shadow-xl shadow-amber-900/5">
              <p className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-amber-800">
                <i className="bi bi-exclamation-triangle-fill" aria-hidden /> Se mandó
              </p>
              <p className="mt-4 text-3xl font-extrabold text-deep">Cable del 10</p>
              <p className="mt-1 text-lg text-amber-900/80">50 metros</p>
            </div>
          </Reveal>
        </div>
      </section>

      <section className="bg-mist/60 py-24">
        <div className="mx-auto max-w-6xl px-5">
          <Reveal className="mx-auto max-w-2xl text-center">
            <p className="text-sm font-bold uppercase tracking-[0.25em] text-coral">Cómo funciona</p>
            <h2 className="mt-3 text-3xl font-extrabold text-deep sm:text-5xl">Tres pasos, un ticket</h2>
          </Reveal>
          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {steps.map((s, i) => (
              <Reveal key={s.title} delay={i * 0.15}>
                <SpotlightCard theme="light" spotlightColor="#ff7a5c" className="h-full rounded-3xl p-8">
                  <span className="grid size-14 place-items-center rounded-2xl bg-petrol text-2xl text-white">
                    <i className={`bi ${s.icon}`} aria-hidden />
                  </span>
                  <p className="mt-6 text-sm font-bold text-coral">Paso {i + 1}</p>
                  <h3 className="mt-1 text-xl font-extrabold text-deep">{s.title}</h3>
                  <p className="mt-3 leading-relaxed text-petrol/80">{s.text}</p>
                </SpotlightCard>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-24">
        <Reveal className="mx-auto mb-12 max-w-2xl text-center">
          <p className="text-sm font-bold uppercase tracking-[0.25em] text-coral">Resultados</p>
          <h2 className="mt-3 text-3xl font-extrabold text-deep sm:text-5xl">Medidos, no prometidos</h2>
        </Reveal>
        <Results />
      </section>

      <section className="bg-deep py-24 text-white">
        <div className="mx-auto max-w-6xl px-5 text-center">
          <Reveal>
            <p className="text-sm font-bold uppercase tracking-[0.25em] text-coral-soft">El equipo</p>
            <h2 className="mt-3 text-3xl font-extrabold sm:text-5xl">Equipo 1 · RNAP Hack 2026</h2>
          </Reveal>
          <div className="mt-12 flex flex-wrap justify-center gap-4">
            {team.map((name, i) => (
              <Reveal key={name} delay={i * 0.1}>
                <div className="flex items-center gap-3 rounded-full bg-white/10 py-3 pe-7 ps-3 backdrop-blur">
                  <span className="grid size-11 place-items-center rounded-full bg-coral text-lg font-extrabold text-deep">{name[0]}</span>
                  <span className="text-lg font-bold">{name}</span>
                </div>
              </Reveal>
            ))}
          </div>
          <Reveal className="mt-14">
            <Link to="/app" className="inline-flex items-center gap-2 rounded-full bg-coral px-8 py-4 text-lg font-extrabold text-deep transition hover:bg-coral-soft">
              <i className="bi bi-mic-fill" aria-hidden /> Probar Receipt
            </Link>
          </Reveal>
        </div>
      </section>
    </div>
  )
}
