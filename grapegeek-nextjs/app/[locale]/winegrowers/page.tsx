import type { Metadata } from 'next'
import { getDatabase } from '@/lib/database'
import WinegrowersIndex from '@/components/winegrower/WinegrowersIndex'
import { type Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  const db = getDatabase();
  const stats = db.getStats();
  return {
    title: `${t('winegrowers.title')} | GrapeGeek`,
    description: t('winegrowers.subtitle', { count: stats.total_winegrowers }),
  };
}

export default function WinegrowersPage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const db = getDatabase()
  const winegrowers = db.getAllWinegrowers()
  const stats = db.getStats()

  // Get unique countries and states for filters
  const countries = Array.from(new Set(winegrowers.map(w => w.country))).sort()
  const states = Array.from(new Set(winegrowers.map(w => w.state_province))).sort()

  return <WinegrowersIndex winegrowers={winegrowers} countries={countries} states={states} stats={stats} locale={locale} />
}
