import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import 'flag-icons/css/flag-icons.min.css'
import Header from '@/components/Header'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'GrapeGeek - North American Winegrower Database',
  description: 'Comprehensive database of winegrowers and grape varieties in northeastern North America',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          integrity="sha512-iecdLmaskl7CVkqkXNQ/ZH/XLlvWZOJyj7Yy7tcenmpD1ypASozpmT/E0iPtmFIB46ZmdtAc9eNBvH0H/ZpiBw=="
          crossOrigin="anonymous"
          referrerPolicy="no-referrer"
        />
      </head>
      <body className={inter.className}>
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="border-t mt-12 py-3 text-center text-gray-600">
          <p>GrapeGeek © {new Date().getFullYear()}</p>
        </footer>
      </body>
    </html>
  )
}
