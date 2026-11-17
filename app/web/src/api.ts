export interface Product {
  id: string
  nombre: string
  categoria: string
  unidad: string
  medida: string
  siblings: string[]
}

export interface TicketData {
  cliente: string
  producto_id: string
  producto: string
  cantidad: number | null
  medida: string
  hora_entrega: string
  producto_solicitado?: string | null
  fuera_de_catalogo?: boolean
}

export interface SiblingOption {
  id: string
  nombre: string
  medida: string
}

export interface ProcessResult {
  transcription: string
  ticket: TicketData
  review_fields: string[]
  extra_products: unknown[]
  sibling_options: SiblingOption[]
  used_fallback: boolean
  timings: { transcription: number; extraction: number; total: number }
}

export interface Order {
  timestamp: string
  cliente: string
  producto_id: string
  producto: string
  cantidad: number
  medida: string
  hora_entrega: string
}

export interface Metric {
  name: string
  mode: string
  split: string
  notes: number
  wer: number
  fields_correct: number
  total_seconds_mean: number
}

export interface OrderPayload {
  cliente: string
  producto_id: string
  cantidad: number
  medida: string
  hora_entrega: string
}

export interface InboxCustomer {
  name: string
  username: string | null
  chat_id: number
}

export interface InboxItem {
  id: string
  received_at: string
  source: string
  customer: InboxCustomer
  status: 'pending' | 'accepted' | 'rejected'
  audio_url: string
  result: ProcessResult
}

export interface Reply {
  id: string
  label: string
  text: string
}

export interface TelegramStatus {
  enabled: boolean
  bot_username: string | null
}

export interface AcceptPayload {
  cliente: string
  producto_id: string | null
  producto_solicitado: string | null
  cantidad: number
  medida: string
  hora_entrega: string
  reply: string
}

async function parse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = ''
    try {
      const body = await res.json()
      detail = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail)
    } catch {
      detail = ''
    }
    throw new Error(detail || `Error ${res.status}`)
  }
  return res.json() as Promise<T>
}

async function request<T>(input: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(input, init)
  } catch {
    throw new Error('No se pudo conectar con el servidor. Verifica que este encendido.')
  }
  return parse<T>(res)
}

export const api = {
  catalog: () => request<Product[]>('/api/catalog'),
  metrics: () => request<Metric[]>('/api/metrics'),
  orders: () => request<Order[]>('/api/orders'),
  process: (audio: Blob, filename: string) => {
    const form = new FormData()
    form.append('audio', audio, filename)
    return request<ProcessResult>('/api/process', { method: 'POST', body: form })
  },
  confirm: (payload: OrderPayload) =>
    request<Order[]>('/api/orders', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  inbox: () => request<InboxItem[]>('/api/inbox'),
  replies: () => request<Reply[]>('/api/replies'),
  telegram: () => request<TelegramStatus>('/api/telegram'),
  acceptInbox: (id: string, payload: AcceptPayload) =>
    request<InboxItem>(`/api/inbox/${id}/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),
  rejectInbox: (id: string, reply: string) =>
    request<InboxItem>(`/api/inbox/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reply }),
    }),
}
