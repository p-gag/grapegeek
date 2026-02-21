import type { Metadata } from 'next';
import { getDatabase } from '@/lib/database';
import { Grape, Wine, MapPin, Building2, Globe, Database } from 'lucide-react';
import StatBox from '@/components/stats/StatBox';
import ChartCard from '@/components/stats/ChartCard';
import TopVarietiesList from '@/components/stats/TopVarietiesList';
import TopStatesList from '@/components/stats/TopStatesList';
import CountryChart from '@/components/stats/CountryChart';
import SpeciesChart from '@/components/stats/SpeciesChart';
import BerryColorChart from '@/components/stats/BerryColorChart';

export const metadata: Metadata = {
  title: 'Statistics & Analytics | GrapeGeek',
  description: 'Comprehensive statistics and analytics for cold-climate wine winegrowers and grape varieties across North America',
};

export default function StatsPage() {
  const db = getDatabase();
  const stats = db.getStats();
  const topVarieties = db.getTopVarietiesByUsage(20);

  // Prepare chart data
  const countryData = Object.entries(stats.countries)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const speciesData = Object.entries(stats.species)
    .map(([name, value]) => ({ name, value }))
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
        <h1 className="text-4xl font-bold mb-4">Statistics & Analytics</h1>
        <p className="text-gray-600 text-lg">
          Comprehensive data insights on cold-climate wine winegrowers and grape varieties across North America
        </p>
      </div>

      {/* Overall Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
        <StatBox
          icon={<Building2 size={40} />}
          label="Winegrowers"
          value={stats.total_winegrowers}
          subtext={`${stats.geolocated_winegrowers} geolocated`}
        />
        <StatBox
          icon={<Grape size={40} />}
          label="Grape Varieties"
          value={stats.total_varieties}
          subtext={`${stats.true_grapes} true grapes`}
        />
        <StatBox
          icon={<Wine size={40} />}
          label="Wine Products"
          value={stats.total_wines}
        />
        <StatBox
          icon={<Globe size={40} />}
          label="Countries"
          value={Object.keys(stats.countries).length}
        />
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
        <StatBox
          icon={<MapPin size={32} />}
          label="States/Provinces"
          value={Object.keys(stats.top_states_provinces).length}
          size="small"
        />
        <StatBox
          icon={<Grape size={32} />}
          label="Grape Species"
          value={Object.keys(stats.species).length}
          size="small"
        />
        <StatBox
          icon={<Globe size={32} />}
          label="With Websites"
          value={stats.winegrowers_with_websites}
          subtext={`${Math.round((stats.winegrowers_with_websites / stats.total_winegrowers) * 100)}% of winegrowers`}
          size="small"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        <ChartCard title="Winegrowers by Country">
          <CountryChart data={countryData} />
        </ChartCard>

        <ChartCard title="Varieties by Species">
          <SpeciesChart data={speciesData} />
        </ChartCard>

        <ChartCard title="Top States/Provinces">
          <TopStatesList data={stateData} />
        </ChartCard>

        <ChartCard title="Varieties by Berry Color">
          <BerryColorChart data={berryColorData} />
        </ChartCard>
      </div>

      {/* Top Lists Section */}
      <div className="grid grid-cols-1 gap-8">
        <ChartCard title="Most Popular Grape Varieties">
          <TopVarietiesList varieties={topVarieties} />
        </ChartCard>
      </div>

      {/* Data Quality Section */}
      <div className="mt-12 bg-[#F5F6FA] rounded-xl p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Database size={28} />
          Data Quality
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">Geolocation Coverage</p>
            <p className="text-2xl font-bold text-brand">
              {Math.round((stats.geolocated_winegrowers / stats.total_winegrowers) * 100)}%
            </p>
            <p className="text-gray-500 text-xs mt-1">
              {stats.geolocated_winegrowers} of {stats.total_winegrowers} winegrowers
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">Website Information</p>
            <p className="text-2xl font-bold text-brand-light">
              {Math.round((stats.winegrowers_with_websites / stats.total_winegrowers) * 100)}%
            </p>
            <p className="text-gray-500 text-xs mt-1">
              {stats.winegrowers_with_websites} with websites
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg">
            <p className="text-gray-600 text-sm mb-1">True Grape Coverage</p>
            <p className="text-2xl font-bold text-brand">
              {Math.round((stats.true_grapes / stats.total_varieties) * 100)}%
            </p>
            <p className="text-gray-500 text-xs mt-1">
              {stats.true_grapes} verified grape varieties
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
