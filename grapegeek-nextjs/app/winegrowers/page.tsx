import type { Metadata } from 'next'
import { getDatabase } from '@/lib/database'
import WinegrowersIndex from '@/components/winegrower/WinegrowersIndex'

export const metadata: Metadata = {
  title: 'Winegrowers | GrapeGeek',
  description: 'Browse cold-climate winegrowers across northeastern North America',
}

export default function WinegrowersPage() {
  const db = getDatabase()
  const winegrowers = db.getAllWinegrowers()
  const stats = db.getStats()

  // Get unique countries and states for filters
  const countries = Array.from(new Set(winegrowers.map(w => w.country))).sort()
  const states = Array.from(new Set(winegrowers.map(w => w.state_province))).sort()

  return <WinegrowersIndex winegrowers={winegrowers} countries={countries} states={states} stats={stats} />
}
