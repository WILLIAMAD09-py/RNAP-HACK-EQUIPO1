import { useEffect, useState } from 'react'
import { api, type Product } from '../../api'
import { SectionTitle } from './Reveal'

const icons: Record<string, string> = {
  cable: 'bi-lightning-charge-fill',
  tubo: 'bi-record-circle-fill',
  acero: 'bi-layers-fill',
  materiales: 'bi-bricks',
  pintura: 'bi-palette-fill',
  fijaciones: 'bi-gear-fill',
  electrico: 'bi-plug-fill',
  plomeria: 'bi-droplet-fill',
}

const normalize = (s: string) => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()

function Chip({ p }: { p: Product }) {
  return (
    <span className="mx-2 inline-flex shrink-0 items-center gap-3 rounded-full bg-white px-5 py-3 text-sm font-bold text-deep shadow-md shadow-deep/5 ring-1 ring-black/5">
      <i className={`bi ${icons[normalize(p.categoria)] ?? 'bi-box-seam-fill'} text-coral`} aria-hidden />
      {p.nombre}
    </span>
  )
}

export default function CatalogMarquee() {
  const [products, setProducts] = useState<Product[] | null>(null)

  useEffect(() => {
    api.catalog().then(setProducts).catch(() => setProducts([]))
  }, [])

  if (!products || products.length === 0) return null
  const half = Math.ceil(products.length / 2)
  const rows = [products.slice(0, half), products.slice(half)]

  return (
    <section className="overflow-hidden bg-mist/60 py-28">
      <div className="px-4">
        <SectionTitle eyebrow="Catálogo" title={`${products.length} productos que Receipt reconoce`} />
      </div>
      <div className="mt-14 space-y-4 [mask-image:linear-gradient(90deg,transparent,#000_10%,#000_90%,transparent)]">
        {rows.map((row, r) => (
          <div
            key={r}
            className="flex w-max hover:[animation-play-state:paused]"
            style={{ animation: `marquee ${row.length * 3.2}s linear infinite ${r ? 'reverse' : 'normal'}` }}
          >
            {[0, 1].map((k) => (
              <div key={k} className="flex shrink-0" aria-hidden={k === 1}>
                {row.map((p) => (
                  <Chip key={p.id} p={p} />
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
    </section>
  )
}
