import { useCallback, useEffect, useState } from 'react'
import type { Product } from '../api'
import { loadInventory, saveInventory, seedInventory, type StockItem } from '../lib/inventory'

export function useInventory(catalog: Product[]) {
  const [items, setItems] = useState<StockItem[]>(() => loadInventory() ?? [])

  useEffect(() => {
    if (!catalog.length) return
    const timer = window.setTimeout(() => {
      setItems((prev) => {
        const known = new Set(prev.map((i) => i.id))
        const missing = seedInventory(catalog).filter((i) => !known.has(i.id))
        if (!missing.length) return prev
        const next = [...prev, ...missing]
        saveInventory(next)
        return next
      })
    }, 0)
    return () => window.clearTimeout(timer)
  }, [catalog])

  const update = useCallback((fn: (prev: StockItem[]) => StockItem[]) => {
    setItems((prev) => {
      const next = fn(prev)
      saveInventory(next)
      return next
    })
  }, [])

  const setStock = useCallback(
    (id: string, stock: number) => update((prev) => prev.map((i) => (i.id === id ? { ...i, stock: Math.max(0, stock) } : i))),
    [update],
  )

  const deduct = useCallback(
    (id: string, amount: number) =>
      update((prev) => prev.map((i) => (i.id === id ? { ...i, stock: Math.max(0, i.stock - amount) } : i))),
    [update],
  )

  return { items, setStock, deduct }
}
