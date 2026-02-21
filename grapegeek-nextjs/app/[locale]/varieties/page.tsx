import type { Metadata } from 'next'
import { getDatabase } from '@/lib/database'
import VarietiesIndex from '@/components/variety/VarietiesIndex'
import { type Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  const db = getDatabase();
  const stats = db.getStats();
  return {
    title: `${t('varieties.title')} | GrapeGeek`,
    description: t('varieties.subtitle', { count: stats.total_varieties }),
  };
}

export default function VarietiesPage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const db = getDatabase()
  const varieties = db.getAllVarieties(true)
  const stats = db.getStats()

  return <VarietiesIndex varieties={varieties} stats={stats} locale={locale} />
}
