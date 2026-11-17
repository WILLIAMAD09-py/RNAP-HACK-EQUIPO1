import { Link } from 'react-router-dom'
import { motion } from 'motion/react'
import Aurora from '../Aurora'
import Reveal from './Reveal'

const team = ['William', 'Jack', 'Carlos', 'Jesús']

export default function FinalCta() {
  return (
    <>
      <section className="relative isolate overflow-hidden bg-deep py-28 text-white">
        <div className="absolute inset-0 -z-10 opacity-60">
          <Aurora colorStops={['#0e4a5a', '#ff7a5c', '#1b7a8c']} amplitude={0.8} blend={0.6} speed={0.4} />
        </div>
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-deep via-deep/40 to-deep" />
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6">
          <Reveal>
            <h2 className="text-4xl font-extrabold leading-tight tracking-tight sm:text-6xl">Pídelo por Telegram</h2>
            <p className="mx-auto mt-5 max-w-xl text-lg text-white/75">Manda tu nota de voz al bot y el pedido llega a la tienda ya convertido en ticket.</p>
          </Reveal>
          <Reveal delay={0.15} className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <motion.a
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.97 }}
              href="https://t.me/rnyap_bot"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-3 rounded-full bg-coral px-8 py-5 text-xl font-extrabold text-deep shadow-[0_20px_60px_-10px_rgba(255,122,92,0.5)]"
            >
              <i className="bi bi-telegram" aria-hidden /> Abrir @rnyap_bot
            </motion.a>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}>
              <Link to="/app" className="inline-flex items-center gap-3 rounded-full bg-white/10 px-8 py-5 text-xl font-extrabold text-white ring-2 ring-white/30 backdrop-blur">
                <i className="bi bi-mic-fill" aria-hidden /> Probar Receipt
              </Link>
            </motion.div>
          </Reveal>
        </div>
      </section>
      <footer className="bg-deep pb-12 text-white">
        <div className="mx-auto max-w-6xl border-t border-white/10 px-4 pt-10 text-center sm:px-6">
          <div className="flex flex-wrap justify-center gap-3">
            {team.map((name) => (
              <span key={name} className="flex items-center gap-2 rounded-full bg-white/10 py-2 pe-5 ps-2 font-bold">
                <span className="grid size-8 place-items-center rounded-full bg-coral font-extrabold text-deep">{name[0]}</span>
                {name}
              </span>
            ))}
          </div>
          <p className="mt-6 text-sm font-semibold text-white/60">RNAP Hack 2026 · Equipo 1</p>
        </div>
      </footer>
    </>
  )
}
