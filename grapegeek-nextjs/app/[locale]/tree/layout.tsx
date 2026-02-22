import type { Metadata } from 'next';
import { type Locale } from '@/lib/i18n/config';

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  return {
    title: params.locale === 'fr' ? 'Arbre généalogique des cépages' : 'Grape Family Tree',
    description: 'Explore the ancestry and relationships between cold-climate grape varieties with an interactive family tree.',
    alternates: {
      canonical: `https://grapegeek.com/${params.locale}/tree`,
      languages: {
        en: 'https://grapegeek.com/en/tree',
        fr: 'https://grapegeek.com/fr/tree',
      },
    },
  };
}

export default function TreeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // No header for tree page - full screen experience
  return children;
}
