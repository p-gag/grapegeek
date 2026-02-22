import type { Metadata } from 'next';
import { type Locale } from '@/lib/i18n/config';

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  return {
    title: params.locale === 'fr' ? 'Carte des vignerons' : 'Winegrower Map',
    description: 'Interactive map of winegrowers across northeastern North America. Filter by grape variety, wine type, and region.',
    alternates: {
      canonical: `https://grapegeek.com/${params.locale}/map`,
      languages: {
        en: 'https://grapegeek.com/en/map',
        fr: 'https://grapegeek.com/fr/map',
      },
    },
  };
}

export default function MapLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // No header for map page - full screen experience
  return children;
}
