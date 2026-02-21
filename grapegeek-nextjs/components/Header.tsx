import Link from 'next/link'
import { Wine } from 'lucide-react'

export default function Header() {
  return (
    <header className="bg-white border-b sticky top-0 z-50">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-brand">
            <Wine className="w-6 h-6" />
            <span>GrapeGeek</span>
          </Link>

          <ul className="flex items-center gap-6">
            <li>
              <Link href="/varieties" className="text-gray-700 hover:text-brand transition">
                Varieties
              </Link>
            </li>
            <li>
              <Link href="/winegrowers" className="text-gray-700 hover:text-brand transition">
                Winegrowers
              </Link>
            </li>
            <li>
              <Link href="/map" className="text-gray-700 hover:text-brand transition">
                Map
              </Link>
            </li>
            <li>
              <Link href="/stats" className="text-gray-700 hover:text-brand transition">
                Stats
              </Link>
            </li>
            <li>
              <Link href="/about" className="text-gray-700 hover:text-brand transition">
                About
              </Link>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  )
}
