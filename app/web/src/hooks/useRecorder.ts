import { useCallback, useEffect, useRef, useState } from 'react'

export function useRecorder() {
  const [recording, setRecording] = useState(false)
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null)
  const [seconds, setSeconds] = useState(0)
  const recorder = useRef<MediaRecorder | null>(null)
  const stream = useRef<MediaStream | null>(null)
  const ctx = useRef<AudioContext | null>(null)
  const chunks = useRef<Blob[]>([])
  const timer = useRef<number | null>(null)
  const resolver = useRef<((blob: Blob) => void) | null>(null)

  const cleanup = useCallback(() => {
    if (timer.current) window.clearInterval(timer.current)
    stream.current?.getTracks().forEach((t) => t.stop())
    ctx.current?.close().catch(() => undefined)
    stream.current = null
    ctx.current = null
    setAnalyser(null)
    setRecording(false)
  }, [])

  useEffect(() => cleanup, [cleanup])

  const start = useCallback(async () => {
    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error('Este navegador no permite grabar. Usa localhost o HTTPS, o sube un archivo.')
    }
    let media: MediaStream
    try {
      media = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      throw new Error('No tenemos permiso para usar el micrófono. Revisa los permisos del navegador.')
    }
    stream.current = media
    const audioCtx = new AudioContext()
    const node = audioCtx.createAnalyser()
    node.fftSize = 1024
    audioCtx.createMediaStreamSource(media).connect(node)
    ctx.current = audioCtx
    setAnalyser(node)

    chunks.current = []
    const rec = new MediaRecorder(media)
    rec.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.current.push(e.data)
    }
    rec.onstop = () => {
      const blob = new Blob(chunks.current, { type: rec.mimeType || 'audio/webm' })
      cleanup()
      resolver.current?.(blob)
      resolver.current = null
    }
    recorder.current = rec
    rec.start()
    setSeconds(0)
    timer.current = window.setInterval(() => setSeconds((s) => s + 1), 1000)
    setRecording(true)
  }, [cleanup])

  const stop = useCallback(
    () =>
      new Promise<Blob>((resolve) => {
        resolver.current = resolve
        recorder.current?.stop()
      }),
    [],
  )

  return { recording, analyser, seconds, start, stop }
}
