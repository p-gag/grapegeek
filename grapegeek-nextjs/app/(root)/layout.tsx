import { Inter } from 'next/font/google'
import '../globals.css'
import 'flag-icons/css/flag-icons.min.css'
import Header from '@/components/Header'
import { defaultLocale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

const inter = Inter({ subsets: ['latin'] })

export default function RootLocaleLayout({ children }: { children: React.ReactNode }) {
  const t = createTranslator(defaultLocale);

  return (
    <html lang={defaultLocale}>
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw=="
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
        <link rel="canonical" href="https://grapegeek.com/en/" />
        <link rel="alternate" hrefLang="en" href="https://grapegeek.com/en/" />
        <link rel="alternate" hrefLang="fr" href="https://grapegeek.com/fr/" />
        <link rel="alternate" hrefLang="x-default" href="https://grapegeek.com/en/" />
      </head>
      <body className={inter.className}>
        <Header locale={defaultLocale} />
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
