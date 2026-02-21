import type { Metadata } from 'next'
import { defaultLocale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'
import HomePage from '@/app/[locale]/page'

export const metadata: Metadata = {
  title: 'GrapeGeek - North American Winegrower Database',
  description: 'Comprehensive database of winegrowers and grape varieties in northeastern North America',
}

export default function RootPage() {
  return <HomePage params={{ locale: defaultLocale }} />
}
