import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const links = [
  { href: '#como-funciona', label: 'Cómo funciona' },
  { href: '#resultados', label: 'Resultados' },
]

export default function Nav() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-500 ${
        scrolled ? 'border-b border-white/10 bg-deep/70 shadow-lg shadow-deep/20 backdrop-blur-xl' : 'bg-transparent'
      }`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <a href="#top" className="flex items-center gap-2.5 text-lg font-extrabold text-white">
          <span className="grid size-9 place-items-center rounded-xl bg-coral text-deep">
            <i className="bi bi-receipt-cutoff" aria-hidden />
          </span>
          Receipt
        </a>
        <div className="flex items-center gap-1 text-sm font-semibold text-white/80 sm:gap-2">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="hidden rounded-full px-3 py-2 transition hover:bg-white/10 hover:text-white md:block">
              {l.label}
            </a>
          ))}
          <Link to="/tienda" className="rounded-full px-3 py-2 transition hover:bg-white/10 hover:text-white">
            Panel de tienda
          </Link>
          <Link to="/app" className="rounded-full bg-coral px-4 py-2 font-extrabold text-deep transition hover:bg-coral-soft">
            Probar
          </Link>
        </div>
      </div>
    </nav>
  )
}
