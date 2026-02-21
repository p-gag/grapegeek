import Link from 'next/link';
import { Wine, Map, BarChart3, Search } from 'lucide-react';
import { getDatabase } from '@/lib/database';
import StatCard from '@/components/home/StatCard';
import FeatureCard from '@/components/home/FeatureCard';

export default function HomePage() {
  const db = getDatabase();
  const stats = db.getStats();

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-purple-600 via-blue-600 to-green-600 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            GrapeGeek
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-purple-100">
            Discover cold-climate grape varieties and the winegrowers who grow them
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              href="/map"
              className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors"
            >
              Explore Map
            </Link>
            <Link
              href="/varieties"
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-colors"
            >
              Browse Varieties
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Grid */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
          By the Numbers
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={<Wine className="w-12 h-12" />}
            value={stats.total_varieties}
            label="Grape Varieties"
            href="/varieties"
          />
          <StatCard
            icon={<Map className="w-12 h-12" />}
            value={stats.total_winegrowers}
            label="Winegrowers"
            href="/winegrowers"
          />
          <StatCard
            icon={<BarChart3 className="w-12 h-12" />}
            value={Object.keys(stats.countries).length}
            label="Countries"
            href="/stats"
          />
          <StatCard
            icon={<Search className="w-12 h-12" />}
            value={stats.total_wines}
            label="Wine Products"
            href="/stats"
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Explore Cold-Climate Viticulture
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FeatureCard
              title="Interactive Map"
              description="Explore winegrowers across northeastern North America with filtering by variety and location."
              href="/map"
              icon={<Map className="w-12 h-12" />}
            />
            <FeatureCard
              title="Grape Varieties"
              description="Discover cold-hardy hybrid varieties, their parentage, and characteristics."
              href="/varieties"
              icon={<Wine className="w-12 h-12" />}
            />
            <FeatureCard
              title="Statistics"
              description="Analyze trends in variety usage, winegrower distribution, and more."
              href="/stats"
              icon={<BarChart3 className="w-12 h-12" />}
            />
          </div>
        </div>
      </section>
    </div>
  );
}
