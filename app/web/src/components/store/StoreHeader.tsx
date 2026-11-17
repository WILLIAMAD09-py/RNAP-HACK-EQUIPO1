import { Link } from 'react-router-dom'
import type { TelegramStatus } from '../../api'
import { cn } from '../../lib/utils'

interface Props {
  telegram: TelegramStatus | null
  online: boolean
  soundOn: boolean
  onToggleSound: () => void
}

export default function StoreHeader({ telegram, online, soundOn, onToggleSound }: Props) {
  const connected = online && telegram?.enabled
  return (
    <header className="sticky top-0 z-30 border-b border-petrol/10 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-5 py-3">
        <Link to="/" className="flex items-center gap-2.5 font-extrabold text-deep">
          <span className="grid size-9 place-items-center rounded-xl bg-petrol text-white">
            <i className="bi bi-shop" aria-hidden />
          </span>
          <span className="leading-tight">
            Receipt <span className="font-semibold text-petrol/60">· Panel de la tienda</span>
          </span>
        </Link>
        <div className="flex flex-wrap items-center gap-2.5">
          <span
            className={cn(
              'inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-sm font-semibold',
              connected ? 'bg-[#e3efe7] text-[#3d6b52]' : 'bg-mist text-petrol/70',
            )}
          >
            <i className={cn('bi', connected ? 'bi-telegram' : 'bi-telegram opacity-60')} aria-hidden />
            {!online
              ? 'Sin conexión con el servidor'
              : connected
                ? `Bot conectado @${telegram?.bot_username}`
                : 'Bot de Telegram sin configurar'}
          </span>
          <button
            type="button"
            onClick={onToggleSound}
            aria-pressed={soundOn}
            className={cn(
              'inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 text-sm font-semibold transition',
              soundOn
                ? 'border-petrol bg-petrol text-white hover:bg-deep'
                : 'border-petrol/25 bg-white text-petrol hover:border-coral hover:text-coral',
            )}
          >
            <i className={cn('bi', soundOn ? 'bi-volume-up-fill' : 'bi-volume-mute-fill')} aria-hidden />
            {soundOn ? 'Sonido activado' : 'Activar sonido'}
          </button>
        </div>
      </div>
    </header>
  )
}
