export interface ReplyValues {
  cliente: string
  cantidad: number | null
  producto: string
  hora: string
}

export function fillReply(template: string, v: ReplyValues) {
  return template
    .replaceAll('{cliente}', v.cliente || 'cliente')
    .replaceAll('{cantidad}', v.cantidad ? String(v.cantidad) : 'la cantidad pedida')
    .replaceAll('{producto}', v.producto || 'tu producto')
    .replaceAll('{hora}', v.hora || 'la hora acordada')
}
