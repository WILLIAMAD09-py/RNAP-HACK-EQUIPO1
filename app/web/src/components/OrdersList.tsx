import { AnimatePresence, motion } from 'motion/react'
import type { Order } from '../api'

export default function OrdersList({ orders }: { orders: Order[] }) {
  if (orders.length === 0) {
    return (
      <div className="rounded-3xl border-2 border-dashed border-petrol/15 p-8 text-center text-petrol/60">
        <i className="bi bi-inbox text-3xl" aria-hidden />
        <p className="mt-2 font-semibold">Aún no hay pedidos hoy</p>
        <p className="text-sm">Los pedidos confirmados aparecen aquí.</p>
      </div>
    )
  }

  return (
    <ul className="max-h-[28rem] space-y-3 overflow-y-auto pe-1">
      <AnimatePresence initial={false}>
        {orders.map((o) => (
          <motion.li
            key={`${o.timestamp}-${o.producto_id}`}
            layout
            initial={{ opacity: 0, x: 40, scale: 0.95 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 24 }}
            className="flex items-center gap-4 rounded-2xl bg-white p-4 shadow-md shadow-deep/5"
          >
            <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-mist text-lg text-petrol">
              <i className="bi bi-receipt" aria-hidden />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate font-bold text-deep">
                {o.cantidad} x {o.producto}
              </p>
              <p className="truncate text-sm text-petrol/70">
                {o.cliente || 'Sin nombre'}
                {o.hora_entrega ? ` · entrega ${o.hora_entrega}` : ''}
              </p>
            </div>
            <span className="rounded-full bg-coral/15 px-2.5 py-1 text-xs font-bold text-coral">{o.timestamp.slice(11, 16)}</span>
          </motion.li>
        ))}
      </AnimatePresence>
    </ul>
  )
}
