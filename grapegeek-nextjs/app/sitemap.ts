import { MetadataRoute } from 'next';
import { getDatabase } from '@/lib/database';
import { slugify } from '@/lib/utils';

const BASE_URL = 'https://grapegeek.com';
const LOCALES = ['en', 'fr'];

function localizedUrls(path: string, priority: number, changeFrequency: MetadataRoute.Sitemap[number]['changeFrequency']) {
  return LOCALES.map((locale) => ({
    url: `${BASE_URL}/${locale}${path}`,
    lastModified: new Date(),
    changeFrequency,
    priority,
  }));
}

export default function sitemap(): MetadataRoute.Sitemap {
  const db = getDatabase();

  const staticPages = [
    ...localizedUrls('', 1.0, 'weekly'),
    ...localizedUrls('/varieties', 0.9, 'weekly'),
    ...localizedUrls('/winegrowers', 0.9, 'weekly'),
    ...localizedUrls('/map', 0.8, 'weekly'),
    ...localizedUrls('/stats', 0.7, 'monthly'),
    ...localizedUrls('/tree', 0.7, 'monthly'),
    ...localizedUrls('/about', 0.5, 'monthly'),
    ...localizedUrls('/ai-usage', 0.3, 'monthly'),
  ];

  const varietyNames = db.getAllVarietyNames();
  const varietyPages = varietyNames.flatMap((name) =>
    LOCALES.map((locale) => ({
      url: `${BASE_URL}/${locale}/varieties/${slugify(name)}`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.6,
    }))
  );

  const winegrowerSlugs = db.getAllWinegrowerSlugs();
  const winegrowerPages = winegrowerSlugs.flatMap((slug) =>
    LOCALES.map((locale) => ({
      url: `${BASE_URL}/${locale}/winegrowers/${slug}`,
      lastModified: new Date(),
      changeFrequency: 'monthly' as const,
      priority: 0.6,
    }))
  );

  db.close();

  return [...staticPages, ...varietyPages, ...winegrowerPages];
}
