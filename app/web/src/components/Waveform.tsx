import { useEffect, useRef } from 'react'

export default function Waveform({ analyser }: { analyser: AnalyserNode | null }) {
  const canvas = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const el = canvas.current
    if (!el || !analyser) return
    const g = el.getContext('2d')!
    const data = new Uint8Array(analyser.fftSize)
    let raf = 0
    const draw = () => {
      const dpr = window.devicePixelRatio || 1
      const w = el.clientWidth
      const h = el.clientHeight
      if (el.width !== Math.round(w * dpr)) {
        el.width = Math.round(w * dpr)
        el.height = Math.round(h * dpr)
      }
      g.setTransform(dpr, 0, 0, dpr, 0, 0)
      analyser.getByteTimeDomainData(data)
      g.clearRect(0, 0, w, h)
      const bars = 48
      const step = Math.floor(data.length / bars)
      const gap = 4
      const bw = w / bars - gap
      for (let i = 0; i < bars; i++) {
        let peak = 0
        for (let j = 0; j < step; j++) peak = Math.max(peak, Math.abs(data[i * step + j] - 128))
        const bh = Math.min(h, Math.max(4, (peak / 128) * h * 1.6))
        g.fillStyle = i % 5 === 0 ? '#ff7a5c' : '#0e4a5a'
        g.beginPath()
        g.roundRect(i * (bw + gap), (h - bh) / 2, bw, bh, bw / 2)
        g.fill()
      }
      raf = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(raf)
  }, [analyser])

  return <canvas ref={canvas} className="h-20 w-full" aria-label="Forma de onda del audio" />
}
