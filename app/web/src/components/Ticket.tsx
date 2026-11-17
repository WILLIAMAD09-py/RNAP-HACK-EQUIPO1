import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import type { OrderPayload, Product, ProcessResult } from '../api'
import { cn } from '../lib/utils'

type FieldKey = 'cliente' | 'producto_id' | 'cantidad' | 'medida' | 'hora_entrega'

interface Props {
  result: ProcessResult
  catalog: Product[]
  confirming: boolean
  onConfirm: (payload: OrderPayload) => void
}

const labels: Record<FieldKey, string> = {
  cliente: 'Cliente',
  producto_id: 'Producto',
  cantidad: 'Cantidad',
  medida: 'Medida',
  hora_entrega: 'Hora de entrega',
}

const icons: Record<FieldKey, string> = {
  cliente: 'bi-person',
  producto_id: 'bi-box-seam',
  cantidad: 'bi-123',
  medida: 'bi-rulers',
  hora_entrega: 'bi-clock',
}

export default function Ticket({ result, catalog, confirming, onConfirm }: Props) {
  const [form, setForm] = useState({
    cliente: result.ticket.cliente ?? '',
    producto_id: result.ticket.producto_id ?? '',
    cantidad: result.ticket.cantidad == null ? '' : String(result.ticket.cantidad),
    medida: result.ticket.medida ?? '',
    hora_entrega: result.ticket.hora_entrega ?? '',
  })
  const [pending, setPending] = useState<Set<string>>(new Set(result.review_fields))
  const [formError, setFormError] = useState('')

  const product = useMemo(() => catalog.find((p) => p.id === form.producto_id), [catalog, form.producto_id])
  const options = useMemo(() => {
    const own = result.sibling_options.filter((o) => o.id !== form.producto_id)
    const current = catalog.find((p) => p.id === result.ticket.producto_id)
    if (current && current.id !== form.producto_id) {
      return [{ id: current.id, nombre: current.nombre, medida: current.medida }, ...own]
    }
    return own
  }, [result, catalog, form.producto_id])

  const touch = (key: FieldKey) =>
    setPending((prev) => {
      const next = new Set(prev)
      next.delete(key)
      if (key === 'producto_id') next.delete('medida')
      return next
    })

  const set = (key: FieldKey, value: string) => {
    setForm((f) => ({ ...f, [key]: value }))
    touch(key)
    setFormError('')
  }

  const pickProduct = (id: string) => {
    const p = catalog.find((c) => c.id === id)
    setForm((f) => ({ ...f, producto_id: id, medida: p?.medida ?? f.medida }))
    touch('producto_id')
    setFormError('')
  }

  const submit = () => {
    const qty = Number(form.cantidad)
    if (!form.producto_id) return setFormError('Elige un producto antes de confirmar.')
    if (!Number.isFinite(qty) || qty <= 0) return setFormError('La cantidad debe ser mayor que cero.')
    if (form.hora_entrega && !/^\d{2}:\d{2}$/.test(form.hora_entrega)) {
      return setFormError('La hora de entrega debe tener el formato HH:MM.')
    }
    onConfirm({
      cliente: form.cliente.trim(),
      producto_id: form.producto_id,
      cantidad: qty,
      medida: form.medida.trim(),
      hora_entrega: form.hora_entrega,
    })
  }

  const inputClass = (key: FieldKey) =>
    cn(
      'w-full rounded-xl border bg-white px-3.5 py-2.5 text-[15px] font-semibold outline-none transition focus:ring-2',
      pending.has(key)
        ? 'border-doubt-border bg-doubt focus:ring-doubt-border/40'
        : 'border-mist focus:border-petrol focus:ring-petrol/20',
    )

  const field = (key: FieldKey, control: React.ReactNode, index: number) => (
    <motion.div
      key={key}
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.15 + index * 0.12, duration: 0.45, ease: 'easeOut' }}
      className="space-y-1.5"
    >
      <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-petrol/70">
        <i className={cn('bi', icons[key])} aria-hidden />
        {labels[key]}
      </label>
      {control}
      <AnimatePresence>
        {pending.has(key) && (
          <motion.p
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="flex items-center gap-1.5 overflow-hidden text-[13px] font-semibold text-amber-700"
          >
            <i className="bi bi-exclamation-triangle-fill" aria-hidden />
            Confirma este dato
          </motion.p>
        )}
      </AnimatePresence>
    </motion.div>
  )

  const extras = result.extra_products
    .map((e) => {
      if (typeof e === 'string') return e
      if (e && typeof e === 'object') {
        const o = e as Record<string, unknown>
        return String(o.producto ?? o.nombre ?? o.texto ?? '')
      }
      return ''
    })
    .filter(Boolean)

  return (
    <div className="drop-shadow-[0_18px_30px_rgba(8,47,56,0.18)]">
      <div className="receipt-paper rounded-t-3xl bg-white px-6 pb-10 pt-7 sm:px-8">
        <div className="mb-5 border-b-2 border-dashed border-mist pb-4 text-center">
          <p className="text-[11px] font-bold uppercase tracking-[0.3em] text-coral">Ticket de pedido</p>
          <h3 className="mt-1 text-xl font-extrabold text-deep">Ferretería Los Nogales</h3>
          <p className="text-xs text-petrol/60">
            {new Date().toLocaleDateString('es-MX', { weekday: 'long', day: 'numeric', month: 'long' })}
          </p>
        </div>

        <div className="space-y-4">
          {field(
            'cliente',
            <input className={inputClass('cliente')} value={form.cliente} onChange={(e) => set('cliente', e.target.value)} placeholder="Nombre del cliente" />,
            0,
          )}
          {field(
            'producto_id',
            <select className={inputClass('producto_id')} value={form.producto_id} onChange={(e) => pickProduct(e.target.value)}>
              <option value="">Selecciona un producto</option>
              {catalog.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nombre} ({p.id})
                </option>
              ))}
            </select>,
            1,
          )}
          {options.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }} className="-mt-1">
              <p className="mb-2 text-xs font-semibold text-petrol/70">Otras medidas disponibles</p>
              <div className="flex flex-wrap gap-2">
                {options.map((o) => (
                  <motion.button
                    key={o.id}
                    type="button"
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={() => pickProduct(o.id)}
                    className="rounded-full border border-petrol/20 bg-mist px-3.5 py-1.5 text-[13px] font-semibold text-petrol transition hover:border-coral hover:bg-coral/10 hover:text-deep"
                  >
                    {o.medida || o.nombre}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
          <div className="grid grid-cols-2 gap-4">
            {field(
              'cantidad',
              <input className={inputClass('cantidad')} inputMode="decimal" value={form.cantidad} onChange={(e) => set('cantidad', e.target.value)} placeholder="0" />,
              2,
            )}
            {field(
              'medida',
              <input className={inputClass('medida')} value={form.medida} onChange={(e) => set('medida', e.target.value)} placeholder={product?.medida || 'Medida'} />,
              3,
            )}
          </div>
          {product && (
            <p className="-mt-2 text-xs text-petrol/60">
              Unidad: <span className="font-semibold">{product.unidad}</span>
            </p>
          )}
          {field(
            'hora_entrega',
            <input className={inputClass('hora_entrega')} type="time" value={form.hora_entrega} onChange={(e) => set('hora_entrega', e.target.value)} />,
            4,
          )}
        </div>

        {extras.length > 0 && (
          <div className="mt-5 rounded-xl bg-mist p-3 text-[13px] text-petrol">
            <i className="bi bi-plus-circle me-1.5" aria-hidden />
            También se mencionaron: <span className="font-semibold">{extras.join(', ')}</span>
          </div>
        )}

        <AnimatePresence>
          {formError && (
            <motion.p
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="mt-4 rounded-xl bg-red-50 px-3.5 py-2.5 text-sm font-medium text-red-700"
            >
              <i className="bi bi-info-circle me-2" aria-hidden />
              {formError}
            </motion.p>
          )}
        </AnimatePresence>

        <motion.button
          type="button"
          onClick={submit}
          disabled={confirming}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          className="mt-6 flex w-full items-center justify-center gap-2.5 rounded-2xl bg-petrol py-4 text-base font-bold text-white shadow-lg shadow-petrol/25 transition hover:bg-deep disabled:opacity-60"
        >
          {confirming ? (
            <>
              <span className="size-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
              Guardando
            </>
          ) : (
            <>
              <i className="bi bi-check2-circle text-lg" aria-hidden />
              Confirmar pedido
            </>
          )}
        </motion.button>
        {pending.size > 0 && (
          <p className="mt-3 text-center text-xs text-amber-700">
            Quedan {pending.size} dato{pending.size > 1 ? 's' : ''} por revisar
          </p>
        )}
      </div>
    </div>
  )
}
