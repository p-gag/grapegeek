import Link from 'next/link';
import { getDatabase } from '@/lib/database';
import GlobalSearch from '@/components/search/GlobalSearch';
import NoScroll from '@/components/NoScroll';
import type { Metadata } from 'next';
import { type Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';
import type { SearchItem } from '@/lib/types';

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: 'GrapeGeek - North American Winegrower Database',
    description: t('home.hero.subtitle'),
  };
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'Organization',
      '@id': 'https://grapegeek.com/#organization',
      name: 'GrapeGeek',
      url: 'https://grapegeek.com',
      description: 'Comprehensive database of winegrowers and cold-climate grape varieties in northeastern North America.',
    },
    {
      '@type': 'WebSite',
      '@id': 'https://grapegeek.com/#website',
      url: 'https://grapegeek.com',
      name: 'GrapeGeek',
      publisher: { '@id': 'https://grapegeek.com/#organization' },
      potentialAction: {
        '@type': 'SearchAction',
        target: {
          '@type': 'EntryPoint',
          urlTemplate: 'https://grapegeek.com/en/varieties?q={search_term_string}',
        },
        'query-input': 'required name=search_term_string',
      },
    },
  ],
};

export default function HomePage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);
  const db = getDatabase();
  const searchData = db.getSearchData();

  const searchItems: SearchItem[] = [
    ...searchData.varieties,
    ...searchData.winegrowers,
  ];

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <NoScroll />
      {/* Fill the viewport below the sticky header (~65px = py-4 + content) */}
      <section className="relative bg-gradient-to-b from-[#4a3570] to-[#7B56D1] flex flex-col items-center text-white px-4 overflow-hidden h-dvh">
        {/* Dot texture */}
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: 'radial-gradient(circle at 25% 60%, white 1px, transparent 1px), radial-gradient(circle at 75% 30%, white 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }} />

        {/* Top zone (smaller) — title anchored to bottom */}
        <div className="relative flex-[2] flex flex-col items-center justify-end pb-8 w-full max-w-3xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-3">
            GrapeGeek
          </h1>
          <p className="text-purple-200 text-lg md:text-xl max-w-lg">
            {t('home.hero.subtitle')}
          </p>
        </div>

        {/* Search — pinned at vertical midpoint */}
        <div className="relative w-full max-w-3xl px-4">
          <GlobalSearch
            items={searchItems}
            locale={locale}
            placeholder={t('home.search.placeholder')}
            labelVariety={t('home.search.tagVariety')}
            labelWinegrower={t('home.search.tagWinegrower')}
          />
        </div>

        {/* Bottom zone (larger) — link anchored to top */}
        <div className="relative flex-[3] flex flex-col items-center justify-start pt-8">
          <Link
            href={`/${locale}/map`}
            className="bg-white/15 hover:bg-white/25 backdrop-blur-sm text-white px-5 py-2 rounded-full transition-colors font-medium text-sm"
          >
            {t('home.hero.winegrowerMap')}
          </Link>
        </div>
      </section>
    </>
  );
}
