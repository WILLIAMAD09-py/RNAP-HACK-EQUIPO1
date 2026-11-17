import { useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import type { AcceptPayload, InboxItem, Product, Reply } from '../../api'
import type { StockItem } from '../../lib/inventory'
import { fillReply } from '../../lib/replies'
import { cn } from '../../lib/utils'

interface Props {
  item: InboxItem
  catalog: Product[]
  replies: Reply[]
  stock: StockItem | undefined
  onAccept: (item: InboxItem, payload: AcceptPayload) => Promise<void>
  onReject: (item: InboxItem, reply: string) => Promise<void>
}

const fieldBase =
  'w-full rounded-xl border-2 bg-white px-3 py-2 font-extrabold text-deep outline-none transition focus:border-coral'

function timeAgo(iso: string) {
  const diff = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000))
  if (diff < 60) return 'hace unos segundos'
  if (diff < 3600) return `hace ${Math.round(diff / 60)} min`
  return new Date(iso).toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })
}

function Collapsible({ icon, label, children }: { icon: string; label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="rounded-2xl bg-mist/60">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center justify-between px-4 py-2.5 text-sm font-bold text-petrol"
      >
        <span className="flex items-center gap-2">
          <i className={`bi ${icon}`} aria-hidden /> {label}
        </span>
        <i className={cn('bi bi-chevron-down transition-transform', open && 'rotate-180')} aria-hidden />
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function OrderCard({ item, catalog, replies, stock, onAccept, onReject }: Props) {
  const { result, customer } = item
  const initial = result.ticket
  const review = new Set(result.review_fields)

  const [cliente, setCliente] = useState(initial.cliente ?? '')
  const [productoId, setProductoId] = useState(initial.producto_id ?? '')
  const [solicitado, setSolicitado] = useState(initial.producto_solicitado ?? '')
  const [cantidad, setCantidad] = useState<string>(initial.cantidad ? String(initial.cantidad) : '')
  const [medida, setMedida] = useState(initial.medida ?? '')
  const [hora, setHora] = useState(initial.hora_entrega ?? '')
  const [replyId, setReplyId] = useState('confirmado')
  const [customText, setCustomText] = useState<string | null>(null)
  const [busy, setBusy] = useState<'accept' | 'reject' | null>(null)
  const [error, setError] = useState('')

  const product = catalog.find((p) => p.id === productoId)
  const offCatalog = !productoId
  const productName = product?.nombre ?? (solicitado || initial.producto || '')
  const unit = product?.unidad ?? ''
  const qty = Number(cantidad) || 0
  const insufficient = !!stock && !offCatalog && qty > stock.stock

  const values = { cliente, cantidad: qty || null, producto: productName, hora }
  const templateOf = (id: string) => fillReply(replies.find((r) => r.id === id)?.text ?? '', values)
  const message = customText ?? templateOf(replyId)

  const doubtful = (name: string) =>
    review.has(name) && !(name === 'producto_id' && !offCatalog && productoId !== (initial.producto_id ?? ''))
  const field = (name: string) => cn(fieldBase, doubtful(name) ? 'border-doubt-border bg-doubt' : 'border-petrol/15')

  const pickProduct = (id: string) => {
    setProductoId(id)
    const p = catalog.find((c) => c.id === id)
    if (p) setMedida(p.medida)
  }

  const pickReply = (id: string) => {
    setReplyId(id)
    setCustomText(null)
  }

  const accept = async () => {
    if (!qty) {
      setError('Indica la cantidad antes de dar de alta.')
      return
    }
    setBusy('accept')
    setError('')
    try {
      await onAccept(item, {
        cliente,
        producto_id: productoId || null,
        producto_solicitado: offCatalog ? solicitado || null : null,
        cantidad: qty,
        medida,
        hora_entrega: hora,
        reply: message,
      })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo dar de alta el pedido.')
      setBusy(null)
    }
  }

  const reject = async () => {
    setBusy('reject')
    setError('')
    const text = replyId === 'confirmado' && customText === null ? templateOf('rechazado') : message
    try {
      await onReject(item, text)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'No se pudo rechazar el pedido.')
      setBusy(null)
    }
  }

  return (
    <motion.article
      layout
      initial={{ opacity: 0, y: -24, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 80 }}
      transition={{ type: 'spring', stiffness: 260, damping: 24 }}
      className="overflow-hidden rounded-3xl border border-petrol/10 bg-white shadow-[0_10px_40px_-18px_rgba(8,47,56,0.35)]"
    >
      <div className="flex items-center justify-between gap-3 bg-deep px-5 py-3 text-white">
        <span className="flex items-center gap-2.5 font-bold">
          <span className="grid size-8 place-items-center rounded-full bg-coral text-deep">
            <i className="bi bi-person-fill" aria-hidden />
          </span>
          {customer.name}
          {customer.username && <span className="font-medium text-white/60">@{customer.username}</span>}
        </span>
        <span className="flex items-center gap-1.5 text-sm text-white/70">
          <i className="bi bi-telegram" aria-hidden /> {timeAgo(item.received_at)}
        </span>
      </div>

      <div className="space-y-4 p-5">
        <div className="grid gap-4 md:grid-cols-[1.6fr_1fr_1fr]">
          <label className="block">
            <span className="mb-1.5 flex flex-wrap items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-petrol/60">
              <i className="bi bi-box-seam" aria-hidden /> Qué
              {offCatalog && (
                <span className="rounded-full bg-coral px-2 py-0.5 text-[11px] font-extrabold normal-case tracking-normal text-deep">
                  Fuera de catálogo
                </span>
              )}
            </span>
            {offCatalog && (
              <input
                value={solicitado}
                onChange={(e) => setSolicitado(e.target.value)}
                placeholder="Producto pedido"
                className={cn(field('producto_id'), 'text-xl')}
              />
            )}
            <select
              value={productoId}
              onChange={(e) => pickProduct(e.target.value)}
              className={cn(field('producto_id'), 'text-lg', offCatalog && 'mt-2 text-sm font-semibold')}
              aria-label="Producto del catálogo"
            >
              <option value="">{offCatalog ? 'Vincular con un producto del catálogo...' : 'Fuera de catálogo'}</option>
              {catalog.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre}
                </option>
              ))}
            </select>
          </label>

          <label className="block">
            <span className="mb-1.5 flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-petrol/60">
              <i className="bi bi-123" aria-hidden /> Cuánto
            </span>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={0}
                value={cantidad}
                onChange={(e) => setCantidad(e.target.value)}
                className={cn(field('cantidad'), 'text-2xl')}
              />
              {unit && <span className="text-sm font-bold text-petrol">{unit}s</span>}
            </div>
          </label>

          <label className="block">
            <span className="mb-1.5 flex items-center gap-2 text-xs font-extrabold uppercase tracking-wider text-petrol/60">
              <i className="bi bi-clock" aria-hidden /> Para cuándo
            </span>
            <input type="time" value={hora} onChange={(e) => setHora(e.target.value)} className={cn(field('hora_entrega'), 'text-2xl')} />
          </label>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block">
            <span className="mb-1 block text-xs font-bold text-petrol/60">Cliente</span>
            <input value={cliente} onChange={(e) => setCliente(e.target.value)} className={cn(field('cliente'), 'text-base')} />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-bold text-petrol/60">Medida</span>
            <input value={medida} onChange={(e) => setMedida(e.target.value)} className={cn(field('medida'), 'text-base')} />
          </label>
        </div>

        {review.size > 0 && (
          <p className="flex items-center gap-2 text-sm font-semibold text-amber-700">
            <i className="bi bi-exclamation-triangle-fill" aria-hidden />
            Revisa los campos en amarillo antes de dar de alta.
          </p>
        )}

        <div className="grid gap-2 sm:grid-cols-2">
          <Collapsible icon="bi-play-circle-fill" label="Escuchar nota">
            <audio controls preload="none" src={item.audio_url} className="w-full" />
          </Collapsible>
          <Collapsible icon="bi-chat-left-text" label="Ver transcripción">
            <p className="text-sm italic text-deep">"{result.transcription}"</p>
          </Collapsible>
        </div>

        {insufficient && stock && (
          <div className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-doubt-border bg-doubt px-4 py-3 text-sm font-semibold text-amber-900">
            <span className="flex items-center gap-2">
              <i className="bi bi-exclamation-triangle-fill" aria-hidden />
              Existencia insuficiente: hay {stock.stock} {stock.unidad}s y piden {qty}.
            </span>
            <button
              type="button"
              onClick={() => pickReply('sin_existencia')}
              className="rounded-full bg-amber-900 px-3 py-1 text-xs font-bold text-white hover:bg-deep"
            >
              Usar respuesta "sin existencia"
            </button>
          </div>
        )}

        <div className="rounded-2xl border border-petrol/10 bg-cream p-4">
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <span className="flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-petrol/60">
              <i className="bi bi-send-fill" aria-hidden /> Respuesta al cliente
            </span>
            <select
              value={replyId}
              onChange={(e) => pickReply(e.target.value)}
              className="ml-auto rounded-full border border-petrol/20 bg-white px-3 py-1 text-sm font-semibold text-petrol outline-none focus:border-coral"
              aria-label="Respuesta predefinida"
            >
              {replies.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          <textarea
            value={message}
            onChange={(e) => setCustomText(e.target.value)}
            rows={2}
            className="w-full resize-y rounded-xl border border-petrol/15 bg-white p-3 text-sm text-deep outline-none focus:border-coral"
            aria-label="Vista previa del mensaje"
          />
        </div>

        {error && (
          <p role="alert" className="flex items-center gap-2 text-sm font-semibold text-red-700">
            <i className="bi bi-x-circle-fill" aria-hidden /> {error}
          </p>
        )}

        <div className="flex flex-wrap gap-3">
          <button
            type="button"
            onClick={accept}
            disabled={busy !== null}
            className="inline-flex flex-1 items-center justify-center gap-2 rounded-full bg-petrol px-6 py-3 text-base font-extrabold text-white transition hover:bg-deep disabled:opacity-50"
          >
            <i className="bi bi-check-circle-fill" aria-hidden />
            {busy === 'accept' ? 'Guardando...' : insufficient ? 'Dar de alta de todos modos' : 'Dar de alta'}
          </button>
          <button
            type="button"
            onClick={reject}
            disabled={busy !== null}
            className="inline-flex items-center justify-center gap-2 rounded-full border-2 border-coral px-6 py-3 text-base font-extrabold text-coral transition hover:bg-coral hover:text-deep disabled:opacity-50"
          >
            <i className="bi bi-x-circle" aria-hidden />
            {busy === 'reject' ? 'Enviando...' : 'Rechazar'}
          </button>
        </div>
      </div>
    </motion.article>
  )
}
