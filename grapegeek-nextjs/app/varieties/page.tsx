import type { Metadata } from 'next'
import { getDatabase } from '@/lib/database'
import VarietiesIndex from '@/components/variety/VarietiesIndex'

export const metadata: Metadata = {
  title: 'Grape Varieties | GrapeGeek',
  description: 'Browse all cold-climate grape varieties grown in northeastern North America',
}

export default function VarietiesPage() {
  const db = getDatabase()
  const varieties = db.getAllVarieties(true)
  const stats = db.getStats()

  return <VarietiesIndex varieties={varieties} stats={stats} />
}
