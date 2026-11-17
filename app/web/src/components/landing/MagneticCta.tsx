import { useRef } from 'react'
import { Link } from 'react-router-dom'
import { motion, useMotionValue, useSpring } from 'motion/react'
import StarBorder from '../StarBorder'

export default function MagneticCta() {
  const ref = useRef<HTMLDivElement>(null)
  const x = useSpring(useMotionValue(0), { stiffness: 200, damping: 15 })
  const y = useSpring(useMotionValue(0), { stiffness: 200, damping: 15 })

  const move = (e: React.MouseEvent) => {
    const r = ref.current!.getBoundingClientRect()
    x.set((e.clientX - (r.left + r.width / 2)) * 0.25)
    y.set((e.clientY - (r.top + r.height / 2)) * 0.35)
  }
  const leave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <div ref={ref} onMouseMove={move} onMouseLeave={leave} className="inline-block py-4 sm:p-4">
      <motion.div style={{ x, y }} whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
        <StarBorder
          as={Link}
          to="/app"
          color="#ff7a5c"
          trailColor="#ffb4a2"
          radius={44}
          thickness={3}
          backgroundColor="#0e4a5a"
          textColor="#ffffff"
          theme="dark"
          className="shadow-[0_20px_60px_-10px_rgba(255,122,92,0.55)]"
        >
          <span className="flex items-center gap-3 px-6 py-5 text-xl font-extrabold sm:gap-4 sm:px-12 sm:py-7 sm:text-3xl">
            <i className="bi bi-mic-fill" aria-hidden />
            Probar Receipt
            <i className="bi bi-arrow-right" aria-hidden />
          </span>
        </StarBorder>
      </motion.div>
    </div>
  )
}
