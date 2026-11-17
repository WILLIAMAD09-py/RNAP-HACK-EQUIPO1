import { motion } from 'motion/react'
import Reveal, { SectionTitle } from './Reveal'

const card = 'h-full rounded-3xl p-7 shadow-xl shadow-deep/5 ring-1 ring-black/5'

export default function Bento() {
  return (
    <section className="mx-auto max-w-6xl px-4 py-28 sm:px-6">
      <SectionTitle eyebrow="Lo que lo hace distinto" title="Ataca el error real de la ferretería" />
      <div className="mt-16 grid gap-5 md:grid-cols-6">
        <Reveal className="md:col-span-3">
          <motion.div whileHover={{ y: -6 }} className={`${card} bg-doubt`}>
            <span className="grid size-12 place-items-center rounded-2xl bg-doubt-border/30 text-2xl text-amber-800">
              <i className="bi bi-exclamation-triangle-fill" aria-hidden />
            </span>
            <h3 className="mt-5 text-2xl font-extrabold text-deep">Campos dudosos en amarillo</h3>
            <p className="mt-2 text-petrol/80">La medida y la cantidad dudosas se marcan para confirmarlas antes de agregar el pedido.</p>
            <div className="mt-5 rounded-xl bg-white/70 px-4 py-3 ring-2 ring-doubt-border">
              <p className="text-xs font-bold uppercase text-amber-800">Medida</p>
              <p className="font-extrabold text-deep">calibre 12</p>
            </div>
          </motion.div>
        </Reveal>
        <Reveal delay={0.1} className="md:col-span-3">
          <motion.div whileHover={{ y: -6 }} className={`${card} bg-white`}>
            <span className="grid size-12 place-items-center rounded-2xl bg-mist text-2xl text-petrol">
              <i className="bi bi-collection-fill" aria-hidden />
            </span>
            <h3 className="mt-5 text-2xl font-extrabold text-deep">Las otras medidas del catálogo</h3>
            <p className="mt-2 text-petrol/80">Si el producto existe en varias medidas, Receipt ofrece las opciones en un toque.</p>
            <div className="mt-5 flex flex-wrap gap-2">
              {['calibre 8', 'calibre 10', 'calibre 12'].map((m, i) => (
                <span key={m} className={`rounded-full px-4 py-2 text-sm font-bold ${i === 2 ? 'bg-petrol text-white' : 'bg-mist text-petrol'}`}>
                  {m}
                </span>
              ))}
            </div>
          </motion.div>
        </Reveal>
        <Reveal delay={0.05} className="md:col-span-2">
          <motion.div whileHover={{ y: -6 }} className={`${card} bg-white`}>
            <span className="grid size-12 place-items-center rounded-2xl bg-coral/15 text-2xl text-coral">
              <i className="bi bi-question-circle-fill" aria-hidden />
            </span>
            <h3 className="mt-5 text-2xl font-extrabold text-deep">Fuera de catálogo</h3>
            <p className="mt-2 text-petrol/80">Si piden algo que no se vende, aparece tal cual se pidió, sin inventar un producto.</p>
            <p className="mt-5 inline-block rounded-xl border-2 border-dashed border-coral px-4 py-2 font-extrabold text-deep">tornillos M4</p>
          </motion.div>
        </Reveal>
        <Reveal delay={0.15} className="md:col-span-4">
          <motion.div whileHover={{ y: -6 }} className={`${card} bg-gradient-to-br from-petrol to-deep text-white`}>
            <div className="flex flex-col gap-6 sm:flex-row sm:items-center">
              <div className="flex-1">
                <span className="grid size-12 place-items-center rounded-2xl bg-white/15 text-2xl text-coral-soft">
                  <i className="bi bi-telegram" aria-hidden />
                </span>
                <h3 className="mt-5 text-2xl font-extrabold">Telegram directo a la tienda</h3>
                <p className="mt-2 text-white/75">El pedido llega al panel con notificación sonora, y la tienda responde al cliente con mensajes predefinidos.</p>
              </div>
              <div className="space-y-2 text-sm font-semibold sm:w-60">
                <motion.p
                  animate={{ scale: [1, 1.04, 1] }}
                  transition={{ duration: 2.4, repeat: Infinity }}
                  className="flex items-center gap-2 rounded-2xl bg-white/15 px-4 py-3 backdrop-blur"
                >
                  <i className="bi bi-bell-fill text-coral-soft" aria-hidden /> Pedido nuevo
                </motion.p>
                <p className="rounded-2xl bg-coral px-4 py-3 text-deep">Listo, sale a las 15:00</p>
              </div>
            </div>
          </motion.div>
        </Reveal>
      </div>
    </section>
  )
}
