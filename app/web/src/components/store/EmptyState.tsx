import { motion } from 'motion/react'

interface Props {
  icon: string
  title: string
  children?: React.ReactNode
}

export default function EmptyState({ icon, title, children }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center rounded-3xl border-2 border-dashed border-petrol/15 bg-white/60 px-6 py-14 text-center"
    >
      <span className="relative mb-5 grid size-20 place-items-center rounded-full bg-mist text-4xl text-petrol">
        <span className="pulse-ring absolute inset-0 rounded-full border-2 border-petrol/20" />
        <i className={`bi ${icon}`} aria-hidden />
      </span>
      <h2 className="text-2xl font-extrabold text-deep">{title}</h2>
      {children && <div className="mt-2 max-w-md text-petrol/80">{children}</div>}
    </motion.div>
  )
}
