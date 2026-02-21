import Link from 'next/link';
import { Wine, Map, BarChart3, Search } from 'lucide-react';
import { getDatabase } from '@/lib/database';
import StatCard from '@/components/home/StatCard';
import FeatureCard from '@/components/home/FeatureCard';
import type { Metadata } from 'next';
import { type Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: 'GrapeGeek - North American Winegrower Database',
    description: t('home.hero.subtitle'),
  };
}

export default function HomePage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);
  const db = getDatabase();
  const stats = db.getStats();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-brand-dark to-brand text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            {t('home.hero.title')}
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-purple-100">
            {t('home.hero.subtitle')}
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href={`/${locale}/map`}
              className="bg-white text-brand px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors shadow-lg"
            >
              {t('home.hero.exploreMap')}
            </Link>
            <Link
              href={`/${locale}/varieties`}
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
            >
              {t('home.hero.browseVarieties')}
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Grid */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
          {t('home.stats.title')}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={<Wine className="w-12 h-12" />}
            value={stats.total_varieties}
            label={t('home.stats.varieties')}
            href={`/${locale}/varieties`}
          />
          <StatCard
            icon={<Map className="w-12 h-12" />}
            value={stats.total_winegrowers}
            label={t('home.stats.winegrowers')}
            href={`/${locale}/winegrowers`}
          />
          <StatCard
            icon={<BarChart3 className="w-12 h-12" />}
            value={Object.keys(stats.countries).length}
            label={t('home.stats.countries')}
            href={`/${locale}/stats`}
          />
          <StatCard
            icon={<Search className="w-12 h-12" />}
            value={stats.total_wines}
            label={t('home.stats.wines')}
            href={`/${locale}/stats`}
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-[#F5F6FA] py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            {t('home.features.title')}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              title={t('home.features.map.title')}
              description={t('home.features.map.description')}
              href={`/${locale}/map`}
              icon={<Map className="w-12 h-12" />}
              exploreLabel={t('home.features.explore')}
            />
            <FeatureCard
              title={t('home.features.varieties.title')}
              description={t('home.features.varieties.description')}
              href={`/${locale}/varieties`}
              icon={<Wine className="w-12 h-12" />}
              exploreLabel={t('home.features.explore')}
            />
            <FeatureCard
              title={t('home.features.stats.title')}
              description={t('home.features.stats.description')}
              href={`/${locale}/stats`}
              icon={<BarChart3 className="w-12 h-12" />}
              exploreLabel={t('home.features.explore')}
            />
          </div>
        </div>
      </section>
    </div>
  );
}
