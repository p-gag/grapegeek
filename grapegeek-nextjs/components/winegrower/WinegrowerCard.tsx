import { Winegrower } from '@/lib/types';
import Link from 'next/link';
import { MapPin, Wine, ExternalLink } from 'lucide-react';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface WinegrowerCardProps {
  winegrower: Winegrower;
  locale: Locale;
}

export default function WinegrowerCard({ winegrower, locale }: WinegrowerCardProps) {
  const t = createTranslator(locale);

  return (
    <Link href={`/${locale}/winegrowers/${winegrower.slug}`}>
      <div className="border rounded-lg p-4 hover:shadow-lg transition-shadow bg-white h-full flex flex-col">
        <div className="flex items-start gap-3 mb-3">
          <Wine className="w-6 h-6 text-brand flex-shrink-0 mt-1" />
          <div className="flex-1 min-w-0">
            <h3 className="text-xl font-bold mb-1 text-gray-900 break-words">
              {winegrower.business_name}
            </h3>
          </div>
        </div>

        <div className="flex items-start gap-2 text-gray-600 text-sm mb-2">
          <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <div>
            <p>{winegrower.city}, {winegrower.state_province}</p>
            <p className="text-gray-500">{winegrower.country}</p>
          </div>
        </div>

        {winegrower.website && (
          <div className="mt-auto pt-3 border-t">
            <div className="flex items-center gap-1 text-sm text-brand hover:text-brand-hover">
              <ExternalLink className="w-3 h-3" />
              <span className="truncate">{t('winegrowers.card.visitWebsite')}</span>
            </div>
          </div>
        )}

        {winegrower.classification && (
          <div className="mt-2">
            <span className="inline-block px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
              {winegrower.classification}
            </span>
          </div>
        )}
      </div>
    </Link>
  );
}
