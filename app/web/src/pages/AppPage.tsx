import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { AnimatePresence, motion } from 'motion/react'
import ClickSpark, { type ClickSparkHandle } from '../components/ClickSpark'
import Waveform from '../components/Waveform'
import Steps from '../components/Steps'
import Ticket from '../components/Ticket'
import OrdersList from '../components/OrdersList'
import { useRecorder } from '../hooks/useRecorder'
import { api, type Order, type OrderPayload, type ProcessResult, type Product } from '../api'
import { cn } from '../lib/utils'

const formatTime = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`

export default function AppPage() {
  const { recording, analyser, seconds, start, stop } = useRecorder()
  const [catalog, setCatalog] = useState<Product[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [result, setResult] = useState<ProcessResult | null>(null)
  const [resultKey, setResultKey] = useState(0)
  const [processing, setProcessing] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const [dragging, setDragging] = useState(false)
  const [serverDown, setServerDown] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)
  const spark = useRef<ClickSparkHandle>(null)

  const load = useCallback(() => {
    api
      .catalog()
      .then((c) => {
        setCatalog(c)
        setServerDown(false)
      })
      .catch(() => setServerDown(true))
    api.orders().then(setOrders).catch(() => undefined)
  }, [])

  useEffect(load, [load])

  const run = async (blob: Blob, name: string) => {
    setError('')
    setSuccess(false)
    setResult(null)
    setProcessing(true)
    try {
      const res = await api.process(blob, name)
      setResult(res)
      setResultKey((k) => k + 1)
      setServerDown(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No pudimos procesar el audio.')
    } finally {
      setProcessing(false)
    }
  }

  const toggleRecord = async () => {
    setError('')
    if (recording) {
      const blob = await stop()
      const ext = blob.type.includes('ogg') ? 'ogg' : blob.type.includes('mp4') ? 'm4a' : 'webm'
      run(blob, `nota.${ext}`)
      return
    }
    try {
      await start()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No pudimos iniciar la grabación.')
    }
  }

  const onFile = (file?: File) => {
    if (!file) return
    if (!file.type.startsWith('audio/') && !/\.(webm|ogg|wav|mp3|m4a|opus)$/i.test(file.name)) {
      setError('Ese archivo no parece ser un audio. Prueba con wav, mp3, m4a, ogg o webm.')
      return
    }
    run(file, file.name)
  }

  const confirm = async (payload: OrderPayload) => {
    setConfirming(true)
    setError('')
    try {
      const updated = await api.confirm(payload)
      setOrders(updated)
      setSuccess(true)
      setResult(null)
      const w = window.innerWidth
      spark.current?.spark(w / 2, 280)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No pudimos guardar el pedido.')
    } finally {
      setConfirming(false)
    }
  }

  return (
    <ClickSpark ref={spark} sparkColor={['#ff7a5c', '#0e4a5a', '#ffb4a2']} sparkCount={14} sparkRadius={70}>
      <div className="min-h-screen bg-cream">
        <header className="border-b border-petrol/10 bg-white/70 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
            <Link to="/" className="flex items-center gap-2.5 font-extrabold text-deep">
              <span className="grid size-9 place-items-center rounded-xl bg-petrol text-white">
                <i className="bi bi-receipt-cutoff" aria-hidden />
              </span>
              Receipt
            </Link>
            <Link to="/" className="flex items-center gap-1.5 text-sm font-semibold text-petrol hover:text-coral">
              <i className="bi bi-arrow-left" aria-hidden /> Inicio
            </Link>
          </div>
        </header>

        <main className="mx-auto grid max-w-6xl gap-10 px-5 py-10 lg:grid-cols-[1fr_420px]">
          <section className="space-y-8">
            <div>
              <h1 className="text-3xl font-extrabold text-deep sm:text-4xl">Graba el pedido</h1>
              <p className="mt-2 max-w-xl text-petrol/75">
                Habla como lo haría el cliente. Revisaremos cantidad y medida antes de que el pedido se guarde.
              </p>
            </div>

            <AnimatePresence>
              {serverDown && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-start gap-3 rounded-2xl bg-doubt p-4 text-amber-900"
                >
                  <i className="bi bi-wifi-off mt-0.5 text-lg" aria-hidden />
                  <div className="flex-1">
                    <p className="font-bold">No hay conexión con el servidor</p>
                    <p className="text-sm">Enciende el servidor de Receipt (puerto 8000) y vuelve a intentarlo.</p>
                  </div>
                  <button onClick={load} className="rounded-full bg-white px-4 py-1.5 text-sm font-bold text-petrol shadow-sm hover:bg-mist">
                    Reintentar
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <div
              onDragOver={(e) => {
                e.preventDefault()
                setDragging(true)
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault()
                setDragging(false)
                onFile(e.dataTransfer.files[0])
              }}
              className={cn(
                'rounded-[2rem] border-2 border-dashed bg-white p-8 text-center shadow-xl shadow-deep/5 transition sm:p-12',
                dragging ? 'border-coral bg-coral/5' : 'border-petrol/15',
              )}
            >
              <div className="relative mx-auto grid size-36 place-items-center">
                {recording && (
                  <>
                    <span className="pulse-ring absolute inset-0 rounded-full bg-coral/40" />
                    <span className="pulse-ring absolute inset-0 rounded-full bg-coral/40 [animation-delay:0.7s]" />
                    <span className="pulse-ring absolute inset-0 rounded-full bg-coral/40 [animation-delay:1.4s]" />
                  </>
                )}
                <motion.button
                  type="button"
                  onClick={toggleRecord}
                  disabled={processing}
                  whileHover={{ scale: 1.06 }}
                  whileTap={{ scale: 0.94 }}
                  aria-label={recording ? 'Detener grabación' : 'Empezar a grabar'}
                  className={cn(
                    'relative grid size-28 place-items-center rounded-full text-5xl text-white shadow-2xl transition disabled:opacity-50',
                    recording ? 'bg-coral shadow-coral/40' : 'bg-petrol shadow-petrol/40 hover:bg-deep',
                  )}
                >
                  <i className={cn('bi', recording ? 'bi-stop-fill' : 'bi-mic-fill')} aria-hidden />
                </motion.button>
              </div>

              <div className="mt-6 min-h-[7rem]">
                {recording ? (
                  <div>
                    <p className="mb-2 font-mono text-lg font-bold text-coral">{formatTime(seconds)}</p>
                    <Waveform analyser={analyser} />
                    <p className="mt-2 text-sm text-petrol/70">Grabando. Toca el botón para terminar.</p>
                  </div>
                ) : (
                  <div>
                    <p className="text-lg font-bold text-deep">{processing ? 'Procesando tu nota' : 'Toca el micrófono para grabar'}</p>
                    <p className="mt-1 text-sm text-petrol/70">o arrastra un archivo de audio aquí</p>
                    <button
                      type="button"
                      disabled={processing}
                      onClick={() => fileInput.current?.click()}
                      className="mt-4 inline-flex items-center gap-2 rounded-full border border-petrol/20 bg-mist px-5 py-2.5 text-sm font-bold text-petrol transition hover:border-coral hover:bg-coral/10 disabled:opacity-50"
                    >
                      <i className="bi bi-upload" aria-hidden /> Subir audio
                    </button>
                    <input ref={fileInput} type="file" accept="audio/*,.opus,.m4a,.webm" hidden onChange={(e) => {
                      onFile(e.target.files?.[0])
                      e.target.value = ''
                    }} />
                  </div>
                )}
              </div>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="flex items-start gap-3 rounded-2xl bg-red-50 p-4 text-red-800"
                  role="alert"
                >
                  <i className="bi bi-emoji-frown mt-0.5 text-lg" aria-hidden />
                  <p className="flex-1 text-sm font-medium">{error}</p>
                  <button onClick={() => setError('')} aria-label="Cerrar aviso" className="text-red-700/70 hover:text-red-900">
                    <i className="bi bi-x-lg" aria-hidden />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            <AnimatePresence mode="wait">
              {processing && <Steps key="steps" />}
              {success && !processing && (
                <motion.div
                  key="ok"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0 }}
                  className="mx-auto flex max-w-md flex-col items-center gap-3 rounded-3xl bg-white p-8 text-center shadow-xl shadow-deep/10"
                >
                  <motion.span
                    initial={{ scale: 0, rotate: -30 }}
                    animate={{ scale: 1, rotate: 0 }}
                    transition={{ type: 'spring', stiffness: 260, damping: 14 }}
                    className="grid size-20 place-items-center rounded-full bg-petrol text-4xl text-white"
                  >
                    <i className="bi bi-check-lg" aria-hidden />
                  </motion.span>
                  <p className="text-xl font-extrabold text-deep">Pedido agregado a la lista del día</p>
                  <p className="text-sm text-petrol/70">Graba otra nota cuando quieras.</p>
                </motion.div>
              )}
            </AnimatePresence>

            {result && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
                <div className="rounded-3xl bg-white p-6 shadow-lg shadow-deep/5">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <p className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-petrol/70">
                      <i className="bi bi-chat-quote" aria-hidden /> Transcripción
                    </p>
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-mist px-3 py-1 text-xs font-bold text-petrol">
                      <i className="bi bi-stopwatch" aria-hidden /> {result.timings.total.toFixed(1)} s
                    </span>
                  </div>
                  <p className="mt-3 text-lg leading-relaxed text-ink">&ldquo;{result.transcription}&rdquo;</p>
                  {result.used_fallback && (
                    <p className="mt-4 flex items-start gap-2 rounded-xl bg-doubt px-3.5 py-2.5 text-sm font-medium text-amber-900">
                      <i className="bi bi-shield-exclamation mt-0.5" aria-hidden />
                      Usamos el método de respaldo (reglas). Revisa los datos con más cuidado.
                    </p>
                  )}
                </div>
              </motion.div>
            )}
          </section>

          <aside className="space-y-8">
            {result && (
              <div className="mx-auto w-full max-w-md lg:max-w-none">
                <Ticket key={resultKey} result={result} catalog={catalog} confirming={confirming} onConfirm={confirm} />
              </div>
            )}
            <div>
              <h2 className="mb-4 flex items-center gap-2 text-xl font-extrabold text-deep">
                <i className="bi bi-list-check text-coral" aria-hidden /> Pedidos del día
                <span className="ms-auto rounded-full bg-petrol px-2.5 py-0.5 text-xs font-bold text-white">{orders.length}</span>
              </h2>
              <OrdersList orders={orders} />
            </div>
          </aside>
        </main>
      </div>
    </ClickSpark>
  )
}
