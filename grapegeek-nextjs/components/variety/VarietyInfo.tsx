import { GrapeVariety } from '@/lib/types';
import Link from 'next/link';
import { slugify } from '@/lib/utils';
import { Users, Dna, MapPin, Calendar, Droplet } from 'lucide-react';

interface Props {
  variety: GrapeVariety;
}

export default function VarietyInfo({ variety }: Props) {
  const hasParents = variety.parent1_name || variety.parent2_name;

  return (
    <div className="space-y-6">
      {/* Characteristics Card */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Dna className="w-6 h-6 text-brand" />
          Characteristics
        </h2>

        <div className="space-y-4">
          {variety.species && (
            <div className="border-b pb-3">
              <p className="text-sm text-gray-600 mb-1">Species</p>
              <p className="font-semibold text-gray-900">{variety.species}</p>
            </div>
          )}

          {variety.berry_skin_color && (
            <div className="border-b pb-3">
              <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                <Droplet className="w-4 h-4" />
                Berry Skin Color
              </p>
              <p className="font-semibold text-gray-900">{variety.berry_skin_color}</p>
            </div>
          )}

          {variety.sex_of_flower && (
            <div className="border-b pb-3">
              <p className="text-sm text-gray-600 mb-1">Sex of Flower</p>
              <p className="font-semibold text-gray-900">{variety.sex_of_flower}</p>
            </div>
          )}

          {variety.country_of_origin && (
            <div className="border-b pb-3">
              <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                Country of Origin
              </p>
              <p className="font-semibold text-gray-900">{variety.country_of_origin}</p>
            </div>
          )}

          {variety.year_of_crossing && (
            <div className="border-b pb-3">
              <p className="text-sm text-gray-600 mb-1 flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                Year of Crossing
              </p>
              <p className="font-semibold text-gray-900">{variety.year_of_crossing}</p>
            </div>
          )}

          {variety.vivc_assignment_status && (
            <div className="border-b pb-3">
              <p className="text-sm text-gray-600 mb-1">VIVC Status</p>
              <p className="font-semibold text-gray-900">{variety.vivc_assignment_status}</p>
            </div>
          )}
        </div>
      </div>

      {/* Family Tree Card */}
      {hasParents && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Users className="w-6 h-6 text-brand" />
            Parentage
          </h2>

          <div className="space-y-3">
            {variety.parent1_name && (
              <div>
                <p className="text-sm text-gray-600 mb-1">Parent 1</p>
                <Link
                  href={`/varieties/${slugify(variety.parent1_name)}`}
                  className="font-semibold text-brand hover:text-brand-hover hover:underline transition-colors"
                >
                  {variety.parent1_name}
                </Link>
              </div>
            )}

            {variety.parent2_name && (
              <div>
                <p className="text-sm text-gray-600 mb-1">Parent 2</p>
                <Link
                  href={`/varieties/${slugify(variety.parent2_name)}`}
                  className="font-semibold text-brand hover:text-brand-hover hover:underline transition-colors"
                >
                  {variety.parent2_name}
                </Link>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Aliases Card */}
      {variety.aliases.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold mb-4">Alternative Names</h2>
          <div className="flex flex-wrap gap-2">
            {variety.aliases.map((alias) => (
              <span
                key={alias}
                className="inline-block bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium"
              >
                {alias}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
