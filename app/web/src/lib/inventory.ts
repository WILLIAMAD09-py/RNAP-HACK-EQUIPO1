import type { Product } from '../api'

export interface StockItem {
  id: string
  nombre: string
  categoria: string
  unidad: string
  stock: number
  minimo: number
}

const STORAGE_KEY = 'receipt.store.inventory'
const SEED = 20261117

const ranges: Record<string, [number, number, number]> = {
  metro: [60, 400, 40],
  pieza: [15, 160, 15],
  kilo: [10, 120, 10],
  caja: [4, 40, 5],
  bolsa: [8, 70, 8],
  litro: [5, 50, 6],
  cubeta: [3, 25, 4],
  rollo: [4, 40, 5],
  par: [6, 60, 8],
}

function mulberry32(seed: number) {
  let a = seed
  return () => {
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

export function seedInventory(catalog: Product[]): StockItem[] {
  const rand = mulberry32(SEED)
  return catalog.map((p) => {
    const [low, high, minimo] = ranges[p.unidad] ?? [10, 80, 10]
    const stock = rand() < 0.15 ? Math.floor(rand() * minimo) : Math.round(low + rand() * (high - low))
    return { id: p.id, nombre: p.nombre, categoria: p.categoria, unidad: p.unidad, stock, minimo }
  })
}

export function loadInventory(): StockItem[] | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? (parsed as StockItem[]) : null
  } catch {
    return null
  }
}

export function saveInventory(items: StockItem[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  } catch {
    return
  }
}

export function stockLevel(item: StockItem): 'agotado' | 'bajo' | 'ok' {
  if (item.stock <= 0) return 'agotado'
  return item.stock <= item.minimo ? 'bajo' : 'ok'
}
