import { useCallback, useEffect, useRef, useState } from 'react'
import { api, type InboxItem } from '../api'

export function useInbox(onNewPending: (items: InboxItem[]) => void) {
  const [items, setItems] = useState<InboxItem[]>([])
  const [online, setOnline] = useState(true)
  const [loaded, setLoaded] = useState(false)
  const seen = useRef<Set<string> | null>(null)
  const callback = useRef(onNewPending)

  useEffect(() => {
    callback.current = onNewPending
  }, [onNewPending])

  const refresh = useCallback(async () => {
    try {
      const data = await api.inbox()
      setItems(data)
      setOnline(true)
      setLoaded(true)
      if (seen.current === null) {
        seen.current = new Set(data.map((i) => i.id))
        return
      }
      const fresh = data.filter((i) => i.status === 'pending' && !seen.current!.has(i.id))
      data.forEach((i) => seen.current!.add(i.id))
      if (fresh.length) callback.current(fresh)
    } catch {
      setOnline(false)
      setLoaded(true)
    }
  }, [])

  useEffect(() => {
    const first = window.setTimeout(refresh, 0)
    const timer = window.setInterval(refresh, 2000)
    return () => {
      window.clearTimeout(first)
      window.clearInterval(timer)
    }
  }, [refresh])

  const replace = useCallback((item: InboxItem) => {
    setItems((prev) => prev.map((i) => (i.id === item.id ? item : i)))
  }, [])

  return { items, online, loaded, refresh, replace }
}
