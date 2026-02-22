import { GrapeVariety } from '@/lib/types'
import Link from 'next/link'
import { slugify } from '@/lib/utils'
import { Wine, MapPin, Users } from 'lucide-react'
import type { Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

interface Props {
  variety: GrapeVariety
  locale: Locale
}

export default function VarietyCard({ variety, locale }: Props) {
  const t = createTranslator(locale)
  const winegrowers = variety.uses?.length || 0

  return (
    <Link href={`/${locale}/varieties/${slugify(variety.name)}`}>
      <div className="bg-white rounded-xl shadow-brand hover:shadow-brand-hover transition-all duration-200 p-6 h-full border-2 border-transparent hover:border-brand-soft">
        {/* Header */}
        <div className="flex items-start gap-3 mb-4">
          <div className="bg-purple-100 rounded-lg p-2 flex-shrink-0">
            <Wine className="w-6 h-6 text-brand" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold text-gray-900 mb-1 truncate">
              {variety.name}
            </h3>
            {variety.aliases.length > 0 && (
              <p className="text-sm text-gray-500 truncate">
                {t('varieties.card.also')} {variety.aliases[0]}
                {variety.aliases.length > 1 && ` +${variety.aliases.length - 1}`}
              </p>
            )}
          </div>
        </div>

        {/* Details */}
        <div className="space-y-2">
          {variety.species && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="font-semibold">{t('varieties.card.species')}</span>
              <span className="truncate">{variety.species}</span>
            </div>
          )}

          {variety.berry_skin_color && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="font-semibold">{t('varieties.card.color')}</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                variety.berry_skin_color.toLowerCase().includes('white') ||
                variety.berry_skin_color.toLowerCase().includes('blanc')
                  ? 'bg-yellow-100 text-yellow-800'
                  : variety.berry_skin_color.toLowerCase().includes('red') ||
                    variety.berry_skin_color.toLowerCase().includes('noir') ||
                    variety.berry_skin_color.toLowerCase().includes('rouge')
                  ? 'bg-red-100 text-red-800'
                  : variety.berry_skin_color.toLowerCase().includes('rose') ||
                    variety.berry_skin_color.toLowerCase().includes('gris')
                  ? 'bg-pink-100 text-pink-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {variety.berry_skin_color}
              </span>
            </div>
          )}

          {variety.country_of_origin && (
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <MapPin className="w-4 h-4 flex-shrink-0" />
              <span className="truncate">{variety.country_of_origin}</span>
            </div>
          )}

          {winegrowers > 0 && (
            <div className="flex items-center gap-2 text-sm text-brand font-semibold mt-3">
              <Users className="w-4 h-4 flex-shrink-0" />
              <span>{t('varieties.card.winegrowers', { count: winegrowers })}</span>
            </div>
          )}
        </div>

        {/* Footer indicators */}
        <div className="mt-4 pt-4 border-t border-gray-100 flex gap-2">
          {variety.is_grape && (
            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
              {t('varieties.card.trueGrape')}
            </span>
          )}
          {variety.vivc_number && (
            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
              {t('varieties.card.vivc', { number: variety.vivc_number })}
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}
