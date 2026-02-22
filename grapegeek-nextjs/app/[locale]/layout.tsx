import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import '../globals.css'
import 'flag-icons/css/flag-icons.min.css'
import Header from '@/components/Header'
import { locales, type Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

const inter = Inter({ subsets: ['latin'] })

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const { locale } = params;
  return {
    metadataBase: new URL('https://grapegeek.com'),
    title: {
      default: 'GrapeGeek - North American Winegrower Database',
      template: '%s | GrapeGeek',
    },
    description: 'Comprehensive database of winegrowers and grape varieties in northeastern North America',
    openGraph: {
      siteName: 'GrapeGeek',
      locale: locale === 'fr' ? 'fr_CA' : 'en_CA',
      type: 'website',
    },
    twitter: {
      card: 'summary',
      site: '@grapegeek',
    },
    alternates: {
      canonical: `https://grapegeek.com/${locale}/`,
      languages: {
        en: 'https://grapegeek.com/en/',
        fr: 'https://grapegeek.com/fr/',
      },
    },
  };
}

export default function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode
  params: { locale: Locale }
}) {
  const { locale } = params;
  const t = createTranslator(locale);

  return (
    <html lang={locale}>
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw=="
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
        <link rel="alternate" hrefLang="en" href={`https://grapegeek.com/en/`} />
        <link rel="alternate" hrefLang="fr" href={`https://grapegeek.com/fr/`} />
        <link rel="alternate" hrefLang="x-default" href={`https://grapegeek.com/en/`} />
      </head>
      <body className={inter.className}>
        <Header locale={locale} />
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="border-t mt-12 py-3 text-center text-gray-600">
          <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
        </footer>
      </body>
    </html>
  )
}
