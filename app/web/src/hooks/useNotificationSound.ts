import { useCallback, useEffect, useRef, useState } from 'react'

const STORAGE_KEY = 'receipt.store.sound'

function readPreference() {
  try {
    return localStorage.getItem(STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

export function useNotificationSound() {
  const [enabled, setEnabled] = useState(readPreference)
  const ctxRef = useRef<AudioContext | null>(null)
  const enabledRef = useRef(enabled)

  useEffect(() => {
    enabledRef.current = enabled
  }, [enabled])

  const context = useCallback(() => {
    if (!ctxRef.current) {
      const Ctor = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext
      if (!Ctor) return null
      ctxRef.current = new Ctor()
    }
    if (ctxRef.current.state === 'suspended') void ctxRef.current.resume()
    return ctxRef.current
  }, [])

  const tone = useCallback((ctx: AudioContext, freq: number, start: number, length: number) => {
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.type = 'sine'
    osc.frequency.value = freq
    gain.gain.setValueAtTime(0.0001, start)
    gain.gain.exponentialRampToValueAtTime(0.22, start + 0.03)
    gain.gain.exponentialRampToValueAtTime(0.0001, start + length)
    osc.connect(gain).connect(ctx.destination)
    osc.start(start)
    osc.stop(start + length + 0.05)
  }, [])

  const play = useCallback(() => {
    if (!enabledRef.current) return
    const ctx = context()
    if (!ctx) return
    const now = ctx.currentTime
    tone(ctx, 659.25, now, 0.35)
    tone(ctx, 987.77, now + 0.16, 0.55)
  }, [context, tone])

  const toggle = useCallback(() => {
    const next = !enabledRef.current
    setEnabled(next)
    enabledRef.current = next
    try {
      localStorage.setItem(STORAGE_KEY, next ? '1' : '0')
    } catch {
      /* sin almacenamiento */
    }
    if (next) {
      const ctx = context()
      if (ctx) {
        const now = ctx.currentTime
        tone(ctx, 659.25, now, 0.35)
        tone(ctx, 987.77, now + 0.16, 0.55)
      }
    }
  }, [context, tone])

  useEffect(() => {
    if (!enabled) return
    const unlock = () => {
      context()
    }
    window.addEventListener('pointerdown', unlock, { once: true })
    return () => window.removeEventListener('pointerdown', unlock)
  }, [enabled, context])

  return { enabled, toggle, play }
}
