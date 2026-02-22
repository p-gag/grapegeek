import type { Metadata } from 'next';
import { getDatabase } from '@/lib/database';
import { simplifySpeciesName } from '@/lib/utils';
import { Grape, Wine, MapPin, Building2, Globe, Database } from 'lucide-react';
import StatBox from '@/components/stats/StatBox';
import ChartCard from '@/components/stats/ChartCard';
import TopVarietiesList from '@/components/stats/TopVarietiesList';
import TopStatesList from '@/components/stats/TopStatesList';
import CountryChart from '@/components/stats/CountryChart';
import SpeciesChart from '@/components/stats/SpeciesChart';
import BerryColorChart from '@/components/stats/BerryColorChart';
import { type Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: `${t('stats.title')} | GrapeGeek`,
    description: t('stats.subtitle'),
  };
}

export default function StatsPage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);
  const db = getDatabase();
  const stats = db.getStats();
  const topVarieties = db.getTopVarietiesByUsage(20);

  // Prepare chart data
  const countryData = Object.entries(stats.countries)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const speciesData = Object.entries(stats.species)
    .map(([name, value]) => ({ name: simplifySpeciesName(name), value }))
    .sort((a, b) => b.value - a.value);

  const berryColorData = Object.entries(stats.berry_colors)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const stateData = Object.entries(stats.top_states_provinces)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-4">{t('stats.title')}</h1>
        <p className="text-gray-600 text-lg">
          {t('stats.subtitle')}
        </p>
      </div>

      {/* Overall Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
        <StatBox
          icon={<Building2 size={40} />}
          label={t('stats.winegrowers')}
          value={stats.total_winegrowers}
          subtext={t('stats.winegrowers.geolocated', { count: stats.geolocated_winegrowers })}
        />
        <StatBox
          icon={<Grape size={40} />}
          label={t('stats.varieties')}
          value={stats.total_varieties}
          subtext={t('stats.varieties.trueGrapes', { count: stats.true_grapes })}
        />
        <StatBox
          icon={<Wine size={40} />}
          label={t('stats.wines')}
          value={stats.total_wines}
        />
        <StatBox
          icon={<Globe size={40} />}
          label={t('stats.countries')}
          value={Object.keys(stats.countries).length}
        />
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
        <StatBox
          icon={<MapPin size={32} />}
          label={t('stats.statesProvinces')}
          value={Object.keys(stats.top_states_provinces).length}
          size="small"
        />
        <StatBox
          icon={<Grape size={32} />}
          label={t('stats.grapeSpecies')}
          value={Object.keys(stats.species).length}
          size="small"
        />
        <StatBox
          icon={<Globe size={32} />}
          label={t('stats.withWebsites')}
          value={stats.winegrowers_with_websites}
          subtext={t('stats.withWebsites.percent', { percent: Math.round((stats.winegrowers_with_websites / stats.total_winegrowers) * 100) })}
          size="small"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        <ChartCard title={t('stats.charts.byCountry')}>
          <CountryChart data={countryData} />
        </ChartCard>

        <ChartCard title={t('stats.charts.bySpecies')}>
          <SpeciesChart data={speciesData} />
        </ChartCard>

        <ChartCard title={t('stats.charts.topStates')}>
          <TopStatesList data={stateData} />
        </ChartCard>

        <ChartCard title={t('stats.charts.byBerryColor')}>
          <BerryColorChart data={berryColorData} />
        </ChartCard>
      </div>

      {/* Top Lists Section */}
      <div className="grid grid-cols-1 gap-8">
        <ChartCard title={t('stats.charts.mostPopular')}>
          <TopVarietiesList varieties={topVarieties} locale={locale} />
        </ChartCard>
      </div>

      {/* Data Quality Section */}
      <div className="mt-12 bg-[#F5F6FA] rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Database size={28} />
          {t('stats.dataQuality.title')}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">{t('stats.dataQuality.geolocation')}</p>
            <p className="text-2xl font-bold text-brand">
              {Math.round((stats.geolocated_winegrowers / stats.total_winegrowers) * 100)}%
            </p>
            <p className="text-gray-500 text-xs mt-1">
              {t('stats.dataQuality.geolocationDesc', { count: stats.geolocated_winegrowers, total: stats.total_winegrowers })}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">{t('stats.dataQuality.websites')}</p>
            <p className="text-2xl font-bold text-brand-light">
              {Math.round((stats.winegrowers_with_websites / stats.total_winegrowers) * 100)}%
            </p>
            <p className="text-gray-500 text-xs mt-1">
              {t('stats.dataQuality.websitesDesc', { count: stats.winegrowers_with_websites })}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">{t('stats.dataQuality.trueGrapes')}</p>
            <p className="text-2xl font-bold text-brand">
              {Math.round((stats.true_grapes / stats.total_varieties) * 100)}%
            </p>
            <p className="text-gray-500 text-xs mt-1">
              {t('stats.dataQuality.trueGrapesDesc', { count: stats.true_grapes })}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
