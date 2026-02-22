'use client';

import Link from 'next/link'
import { Wine } from 'lucide-react'
import { usePathname } from 'next/navigation'
import type { Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

interface HeaderProps {
  locale: Locale;
}

export default function Header({ locale }: HeaderProps) {
  const t = createTranslator(locale);
  const pathname = usePathname();
  const otherLocale: Locale = locale === 'en' ? 'fr' : 'en';

  // Swap locale prefix in current path
  // Root "/" has no locale prefix, so map directly to the other locale's root
  const alternatePath = pathname === '/'
    ? `/${otherLocale}/`
    : pathname.replace(`/${locale}/`, `/${otherLocale}/`).replace(new RegExp(`^/${locale}$`), `/${otherLocale}`);

  return (
    <header className="bg-white border-b sticky top-0 z-50">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href={`/${locale}/`} className="flex items-center gap-2 text-xl font-bold text-brand">
            <Wine className="w-6 h-6" />
            <span>{t('nav.home')}</span>
          </Link>

          <ul className="flex items-center gap-6">
            <li>
              <Link href={`/${locale}/map`} className="text-gray-700 hover:text-brand transition">
                {t('nav.map')}
              </Link>
            </li>
            <li>
              <Link href={`/${locale}/about`} className="text-gray-700 hover:text-brand transition">
                {t('nav.about')}
              </Link>
            </li>
            <li>
              <Link
                href={alternatePath}
                className="text-sm font-semibold px-2 py-1 rounded border border-brand text-brand hover:bg-brand hover:text-white transition"
                title={t('nav.langSwitchLabel')}
              >
                {t('nav.langSwitch')}
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  )
}
