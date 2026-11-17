import { useCallback, useEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { api, type AcceptPayload, type InboxItem, type Product, type Reply, type TelegramStatus } from '../api'
import StoreHeader from '../components/store/StoreHeader'
import OrderCard from '../components/store/OrderCard'
import InventoryPanel from '../components/store/InventoryPanel'
import EmptyState from '../components/store/EmptyState'
import Toasts, { type ToastData } from '../components/store/Toasts'
import { useInbox } from '../hooks/useInbox'
import { useInventory } from '../hooks/useInventory'
import { useNotificationSound } from '../hooks/useNotificationSound'
import { stockLevel } from '../lib/inventory'
import { cn } from '../lib/utils'

type Tab = 'pendientes' | 'atendidos' | 'inventario'

function HandledRow({ item }: { item: InboxItem }) {
  const t = item.result.ticket
  const accepted = item.status === 'accepted'
  const name = t.producto || t.producto_solicitado || 'Producto sin identificar'
  return (
    <motion.li
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-wrap items-center gap-x-5 gap-y-1 rounded-2xl border border-petrol/10 bg-white px-5 py-3.5"
    >
      <span
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-extrabold',
          accepted ? 'bg-[#e3efe7] text-[#3d6b52]' : 'bg-coral/20 text-red-700',
        )}
      >
        <i className={cn('bi', accepted ? 'bi-check-circle-fill' : 'bi-x-circle-fill')} aria-hidden />
        {accepted ? 'Dado de alta' : 'Rechazado'}
      </span>
      <span className="font-extrabold text-deep">
        {t.cantidad} · {name}
      </span>
      <span className="text-sm text-petrol/70">{item.customer.name}</span>
      {t.hora_entrega && (
        <span className="ml-auto flex items-center gap-1.5 text-sm font-semibold text-petrol">
          <i className="bi bi-clock" aria-hidden /> {t.hora_entrega}
        </span>
      )}
    </motion.li>
  )
}

export default function StorePage() {
  const [tab, setTab] = useState<Tab>('pendientes')
  const [catalog, setCatalog] = useState<Product[]>([])
  const [replies, setReplies] = useState<Reply[]>([])
  const [telegram, setTelegram] = useState<TelegramStatus | null>(null)
  const [toasts, setToasts] = useState<ToastData[]>([])
  const toastId = useRef(0)
  const sound = useNotificationSound()
  const inventory = useInventory(catalog)

  const pushToast = useCallback((text: string, tone: ToastData['tone']) => {
    const id = ++toastId.current
    setToasts((prev) => [...prev, { id, text, tone }])
    window.setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 5000)
  }, [])

  const onNewPending = useCallback(
    (fresh: InboxItem[]) => {
      sound.play()
      fresh.forEach((i) => pushToast(`Nuevo pedido de ${i.customer.name}`, 'new'))
    },
    [sound, pushToast],
  )

  const inbox = useInbox(onNewPending)

  useEffect(() => {
    let alive = true
    const loadStatic = () => {
      api.catalog().then((c) => alive && setCatalog(c)).catch(() => undefined)
      api.replies().then((r) => alive && setReplies(r)).catch(() => undefined)
    }
    const loadTelegram = () => api.telegram().then((t) => alive && setTelegram(t)).catch(() => alive && setTelegram(null))
    const first = window.setTimeout(() => {
      loadStatic()
      void loadTelegram()
    }, 0)
    const timer = window.setInterval(() => {
      void loadTelegram()
      if (!catalog.length || !replies.length) loadStatic()
    }, 10000)
    return () => {
      alive = false
      window.clearTimeout(first)
      window.clearInterval(timer)
    }
  }, [catalog.length, replies.length])

  const pending = inbox.items.filter((i) => i.status === 'pending')
  const handled = inbox.items.filter((i) => i.status !== 'pending')
  const lowCount = inventory.items.filter((i) => stockLevel(i) !== 'ok').length

  const accept = async (item: InboxItem, payload: AcceptPayload) => {
    const updated = await api.acceptInbox(item.id, payload)
    inbox.replace(updated)
    if (payload.producto_id) inventory.deduct(payload.producto_id, payload.cantidad)
    pushToast('Pedido dado de alta y cliente avisado', 'ok')
  }

  const reject = async (item: InboxItem, reply: string) => {
    const updated = await api.rejectInbox(item.id, reply)
    inbox.replace(updated)
    pushToast('Pedido rechazado y cliente avisado', 'warn')
  }

  const tabs: { id: Tab; label: string; icon: string; count: number }[] = [
    { id: 'pendientes', label: 'Pendientes', icon: 'bi-inbox-fill', count: pending.length },
    { id: 'atendidos', label: 'Atendidos hoy', icon: 'bi-clock-history', count: handled.length },
    { id: 'inventario', label: 'Inventario', icon: 'bi-boxes', count: lowCount },
  ]

  return (
    <div className="min-h-screen bg-cream">
      <StoreHeader telegram={telegram} online={inbox.online} soundOn={sound.enabled} onToggleSound={sound.toggle} />
      <Toasts toasts={toasts} />

      <main className="mx-auto max-w-6xl px-5 py-8">
        <div className="mb-6">
          <h1 className="text-3xl font-extrabold text-deep sm:text-4xl">Pedidos de hoy</h1>
          <p className="mt-1 text-petrol/70">Las notas de voz que llegan por Telegram aparecen aquí listas para revisar.</p>
        </div>

        {!inbox.online && inbox.loaded && (
          <div role="alert" className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-red-800">
            <span className="flex items-center gap-2 font-bold">
              <i className="bi bi-wifi-off" aria-hidden /> Sin conexión con el servidor. Reintentando cada 2 segundos.
            </span>
            <button
              type="button"
              onClick={() => void inbox.refresh()}
              className="inline-flex items-center gap-2 rounded-full bg-red-800 px-4 py-1.5 text-sm font-bold text-white hover:bg-red-900"
            >
              <i className="bi bi-arrow-repeat" aria-hidden /> Reintentar ahora
            </button>
          </div>
        )}

        <div role="tablist" className="mb-6 flex gap-2 overflow-x-auto rounded-full bg-white p-1.5 shadow-sm ring-1 ring-petrol/10">
          {tabs.map((t) => (
            <button
              key={t.id}
              role="tab"
              type="button"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={cn(
                'relative flex flex-1 items-center justify-center gap-2 whitespace-nowrap rounded-full px-4 py-2.5 text-sm font-extrabold transition',
                tab === t.id ? 'text-white' : 'text-petrol hover:bg-mist',
              )}
            >
              {tab === t.id && (
                <motion.span layoutId="store-tab" className="absolute inset-0 rounded-full bg-petrol" transition={{ type: 'spring', stiffness: 380, damping: 32 }} />
              )}
              <span className="relative flex items-center gap-2">
                <i className={`bi ${t.icon}`} aria-hidden /> {t.label}
                {t.count > 0 && (
                  <span
                    className={cn(
                      'grid min-w-6 place-items-center rounded-full px-1.5 text-xs font-extrabold',
                      t.id === 'inventario' ? 'bg-doubt text-amber-800' : 'bg-coral text-deep',
                    )}
                  >
                    {t.count}
                  </span>
                )}
              </span>
            </button>
          ))}
        </div>

        {tab === 'pendientes' && (
          <div className="space-y-6">
            <AnimatePresence mode="popLayout">
              {pending.map((item) => (
                <OrderCard
                  key={item.id}
                  item={item}
                  catalog={catalog}
                  replies={replies}
                  stock={inventory.items.find((s) => s.id === item.result.ticket.producto_id)}
                  onAccept={accept}
                  onReject={reject}
                />
              ))}
            </AnimatePresence>
            {!pending.length && inbox.loaded && (
              <EmptyState icon="bi-inbox" title="Sin pedidos por ahora">
                <p>
                  Para probar, manda una nota de voz al bot de Telegram
                  {telegram?.enabled ? ` @${telegram.bot_username}` : ''}, por ejemplo: "Soy Pedro, mándame cincuenta metros de cable del doce para las tres".
                </p>
                {!telegram?.enabled && (
                  <p className="mt-2 text-sm">El bot se enciende al definir TELEGRAM_BOT_TOKEN y reiniciar el servidor.</p>
                )}
              </EmptyState>
            )}
          </div>
        )}

        {tab === 'atendidos' &&
          (handled.length ? (
            <ul className="space-y-3">
              {handled.map((item) => (
                <HandledRow key={item.id} item={item} />
              ))}
            </ul>
          ) : (
            <EmptyState icon="bi-clock-history" title="Aún no hay pedidos atendidos">
              Los pedidos que des de alta o rechaces hoy se listan aquí.
            </EmptyState>
          ))}

        {tab === 'inventario' && <InventoryPanel items={inventory.items} onSetStock={inventory.setStock} />}
      </main>
    </div>
  )
}
