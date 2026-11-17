import { Link } from 'react-router-dom'
import { motion } from 'motion/react'
import Aurora from '../components/Aurora'
import SplitText from '../components/SplitText'
import Nav from '../components/landing/Nav'
import MagneticCta from '../components/landing/MagneticCta'
import PhoneDemo from '../components/landing/PhoneDemo'
import BeforeAfter from '../components/landing/BeforeAfter'
import HowItWorks from '../components/landing/HowItWorks'
import Bento from '../components/landing/Bento'
import CatalogMarquee from '../components/landing/CatalogMarquee'
import Results from '../components/landing/Results'
import FinalCta from '../components/landing/FinalCta'

export default function Landing() {
  return (
    <div id="top" className="overflow-x-clip bg-cream">
      <Nav />
      <section className="relative isolate overflow-hidden bg-deep pb-20 pt-28 text-white">
        <div className="absolute inset-0 -z-10 opacity-80">
          <Aurora colorStops={['#0e4a5a', '#ff7a5c', '#1b7a8c']} amplitude={0.9} blend={0.6} speed={0.5} />
        </div>
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-deep/30 via-transparent to-deep" />
        <div className="mx-auto grid max-w-7xl items-center gap-14 px-4 sm:px-6 lg:grid-cols-[1.15fr_0.85fr]">
          <div className="text-center lg:text-left">
            <motion.p
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-1.5 text-sm font-semibold backdrop-blur"
            >
              <i className="bi bi-whatsapp text-coral-soft" aria-hidden /> Ferretería Los Nogales · Monterrey
            </motion.p>
            <SplitText
              text="De nota de voz a pedido en segundos"
              tag="h1"
              splitType="words"
              trigger="load"
              textAlign="left"
              className="text-4xl font-extrabold leading-[1.05] tracking-tight text-white sm:text-6xl xl:text-7xl"
            />
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.1 }} className="mx-auto mt-6 max-w-xl text-lg text-white/75 sm:text-xl lg:mx-0">
              Graba o sube la nota del cliente. Receipt escribe el ticket y marca qué dato conviene confirmar antes de salir a entregar.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.3, type: 'spring' }}
              className="mt-8 flex flex-col items-center gap-2 lg:items-start"
            >
              <MagneticCta />
              <Link to="/tienda" className="inline-flex items-center gap-2 rounded-full px-5 py-3 text-base font-bold text-white/85 ring-1 ring-white/30 transition hover:bg-white/10">
                <i className="bi bi-shop" aria-hidden /> Ver panel de la tienda
              </Link>
            </motion.div>
          </div>
          <motion.div initial={{ opacity: 0, x: 60 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.6, duration: 1, ease: [0.22, 1, 0.36, 1] }}>
            <PhoneDemo />
          </motion.div>
        </div>
      </section>
      <BeforeAfter />
      <HowItWorks />
      <Bento />
      <CatalogMarquee />
      <Results />
      <FinalCta />
    </div>
  )
}
