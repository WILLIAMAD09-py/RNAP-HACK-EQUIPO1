import { useMemo, useState } from 'react'
import { stockLevel, type StockItem } from '../../lib/inventory'
import { cn } from '../../lib/utils'
import EmptyState from './EmptyState'

interface Props {
  items: StockItem[]
  onSetStock: (id: string, stock: number) => void
}

const badge = {
  agotado: 'bg-red-100 text-red-700',
  bajo: 'bg-doubt text-amber-800',
  ok: 'bg-[#e3efe7] text-[#3d6b52]',
}
const badgeText = { agotado: 'Agotado', bajo: 'Bajo', ok: 'Suficiente' }

export default function InventoryPanel({ items, onSetStock }: Props) {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('')

  const categories = useMemo(() => [...new Set(items.map((i) => i.categoria))].sort(), [items])
  const low = items.filter((i) => stockLevel(i) !== 'ok')
  const shown = items.filter(
    (i) =>
      (!category || i.categoria === category) &&
      `${i.nombre} ${i.id}`.toLowerCase().includes(query.trim().toLowerCase()),
  )

  if (!items.length) {
    return (
      <EmptyState icon="bi-boxes" title="Inventario no disponible">
        Se genera a partir del catálogo cuando hay conexión con el servidor.
      </EmptyState>
    )
  }

  return (
    <div className="space-y-4">
      {low.length > 0 && (
        <div className="rounded-2xl border border-doubt-border bg-doubt p-4 text-amber-900">
          <p className="flex items-center gap-2 font-extrabold">
            <i className="bi bi-exclamation-triangle-fill" aria-hidden />
            {low.length} {low.length === 1 ? 'producto con' : 'productos con'} existencia baja
          </p>
          <p className="mt-1 text-sm">{low.map((i) => i.nombre).join(' · ')}</p>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <div className="relative min-w-60 flex-1">
          <i className="bi bi-search pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-petrol/50" aria-hidden />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar producto o clave"
            className="w-full rounded-full border border-petrol/15 bg-white py-2.5 pl-11 pr-4 text-sm font-semibold outline-none focus:border-coral"
          />
        </div>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          aria-label="Filtrar por categoría"
          className="rounded-full border border-petrol/15 bg-white px-4 py-2.5 text-sm font-semibold text-petrol outline-none focus:border-coral"
        >
          <option value="">Todas las categorías</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto rounded-3xl border border-petrol/10 bg-white">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="bg-mist/70 text-xs uppercase tracking-wider text-petrol/70">
            <tr>
              <th className="px-4 py-3">Clave</th>
              <th className="px-4 py-3">Producto</th>
              <th className="px-4 py-3">Categoría</th>
              <th className="px-4 py-3">Existencia</th>
              <th className="px-4 py-3">Estado</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((i) => {
              const level = stockLevel(i)
              return (
                <tr key={i.id} className={cn('border-t border-petrol/5', level !== 'ok' && 'bg-doubt/30')}>
                  <td className="px-4 py-2.5 font-mono text-xs text-petrol/70">{i.id}</td>
                  <td className="px-4 py-2.5 font-bold text-deep">{i.nombre}</td>
                  <td className="px-4 py-2.5 text-petrol/80">{i.categoria}</td>
                  <td className="px-4 py-2.5">
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        min={0}
                        value={i.stock}
                        onChange={(e) => onSetStock(i.id, Number(e.target.value) || 0)}
                        aria-label={`Existencia de ${i.nombre}`}
                        className="w-20 rounded-lg border border-petrol/15 px-2 py-1 font-bold outline-none focus:border-coral"
                      />
                      <span className="text-petrol/70">{i.unidad}s</span>
                    </div>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={cn('rounded-full px-2.5 py-1 text-xs font-bold', badge[level])}>{badgeText[level]}</span>
                  </td>
                </tr>
              )
            })}
            {!shown.length && (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-petrol/60">
                  Sin resultados para esa búsqueda.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
