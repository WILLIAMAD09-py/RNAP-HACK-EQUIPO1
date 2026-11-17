import { useEffect, useState } from 'react'
import CountUp from '../CountUp'
import { api, type Metric } from '../../api'
import Reveal, { SectionTitle } from './Reveal'

const testRuns = [
  { name: 'baseline_test', label: 'Línea base: Whisper small + reglas' },
  { name: 'pretrained_test', label: 'Preentrenado: Whisper medium + LLM' },
  { name: 'solution_test', label: 'Receipt: solución híbrida' },
]

function Cards() {
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
        {shown.map(({ metric: m, label }, i) => {
          const hero = m.name === 'solution_test'
          return (
            <Reveal key={m.name} delay={i * 0.12}>
              <div className={`h-full rounded-3xl p-7 shadow-xl transition hover:-translate-y-1 ${hero ? 'bg-coral/10 shadow-coral/20 ring-2 ring-coral' : 'bg-white shadow-deep/5'}`}>
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

export default function Results() {
  return (
    <section id="resultados" className="mx-auto max-w-6xl px-4 py-28 sm:px-6">
      <div className="mb-14">
        <SectionTitle eyebrow="Resultados" title="Medidos, no prometidos" />
      </div>
      <Cards />
    </section>
  )
}
