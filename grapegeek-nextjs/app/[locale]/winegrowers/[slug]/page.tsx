import { getDatabase } from '@/lib/database';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import WinegrowerMap from '@/components/winegrower/WinegrowerMap';
import WinegrowerVarieties from '@/components/winegrower/WinegrowerVarieties';
import { type Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface Props {
  params: { locale: Locale; slug: string };
}

// Static generation: pre-render all winegrower pages at build time
export async function generateStaticParams() {
  const db = getDatabase();
  const slugs = db.getAllWinegrowerSlugs();

  return slugs.map((slug) => ({
    slug: slug,
  }));
}

// Generate metadata for SEO
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const t = createTranslator(params.locale);
  const db = getDatabase();
  const winegrower = db.getWinegrowerBySlug(params.slug, true);

  if (!winegrower) {
    return {
      title: `${t('winegrower.notFound.title')} | GrapeGeek`,
      description: t('winegrower.notFound.text'),
    };
  }

  const wineCount = winegrower.wines?.length || 0;
  const description = `${winegrower.business_name} is a winegrower in ${winegrower.city}, ${winegrower.state_province}, ${winegrower.country}. ${wineCount > 0 ? `Produces ${wineCount} wine${wineCount !== 1 ? 's' : ''}.` : ''}`;

  return {
    title: `${winegrower.business_name} - ${winegrower.city}, ${winegrower.state_province} | GrapeGeek`,
    description: description,
    alternates: {
      canonical: `https://grapegeek.com/${params.locale}/winegrowers/${params.slug}`,
      languages: {
        en: `https://grapegeek.com/en/winegrowers/${params.slug}`,
        fr: `https://grapegeek.com/fr/winegrowers/${params.slug}`,
      },
    },
  };
}

const getDomainFavicon = (url: string) => {
  try {
    const domain = new URL(url).hostname;
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`;
  } catch {
    return null;
  }
};

const getSocialIcon = (url: string) => {
  const urlLower = (url || '').toLowerCase();

  if (urlLower.includes('facebook.com')) {
    return { icon: 'fab fa-facebook', color: '#1877F2', platform: 'Facebook' };
  }
  if (urlLower.includes('instagram.com')) {
    return { icon: 'fab fa-instagram', color: '#E4405F', platform: 'Instagram' };
  }
  if (urlLower.includes('twitter.com') || urlLower.includes('x.com')) {
    return { icon: 'fab fa-x-twitter', color: '#000000', platform: 'Twitter/X' };
  }
  if (urlLower.includes('youtube.com')) {
    return { icon: 'fab fa-youtube', color: '#FF0000', platform: 'YouTube' };
  }
  return { icon: 'fas fa-link', color: '#666', platform: 'Social' };
};

export default function WinegrowerDetailPage({ params }: Props) {
  const { locale } = params;
  const db = getDatabase();
  const winegrower = db.getWinegrowerBySlug(params.slug, true);

  if (!winegrower) {
    notFound();
  }

  // Get unique variety names from wines
  const varietyNames = Array.from(
    new Set(
      winegrower.wines?.flatMap(wine =>
        wine.grapes.map(g => g.variety_name)
      ) || []
    )
  );

  // Load photo thumbnails for varieties
  const varietyPhotos = db.getVarietyPhotoThumbnails(varietyNames);
  db.close();

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Winery',
    name: winegrower.business_name,
    address: {
      '@type': 'PostalAddress',
      addressLocality: winegrower.city,
      addressRegion: winegrower.state_province,
      addressCountry: winegrower.country,
    },
    ...(winegrower.website ? { url: winegrower.website } : {}),
    ...(winegrower.latitude && winegrower.longitude ? {
      geo: {
        '@type': 'GeoCoordinates',
        latitude: winegrower.latitude,
        longitude: winegrower.longitude,
      },
    } : {}),
  };

  return (
    <div className="winegrower-page">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {/* Page Header */}
      <div className="winegrower-header">
        <h1 className="winegrower-title">{winegrower.business_name}</h1>
        <p className="winegrower-location">
          📍 {winegrower.city}, {winegrower.state_province}
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="winegrower-content-grid">
        {/* Left Column: Map + Contact */}
        <div className="winegrower-map-column">
          <WinegrowerMap winegrower={winegrower} />
          <div className="winegrower-contact-links">
            {winegrower.website && (
              <a
                href={winegrower.website}
                target="_blank"
                rel="noopener noreferrer"
                className="contact-link website-link"
              >
                {getDomainFavicon(winegrower.website) ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={getDomainFavicon(winegrower.website) || undefined}
                    alt="Website icon"
                    className="website-favicon"
                  />
                ) : (
                  <i className="fas fa-globe"></i>
                )}
                <span>Website</span>
              </a>
            )}

            {winegrower.social_media && winegrower.social_media.length > 0 && (
              winegrower.social_media.map((social, index) => {
                const { icon, color, platform } = getSocialIcon(social);

                return (
                  <a
                    key={index}
                    href={social}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="contact-link social-link"
                    title={platform}
                  >
                    <i className={icon} style={{ color }}></i>
                    <span>{platform}</span>
                  </a>
                );
              })
            )}
          </div>
        </div>

        {/* Right Column: Varieties */}
        <div className="winegrower-info-column">
          <WinegrowerVarieties
            winegrower={winegrower}
            varietyPhotos={Object.fromEntries(varietyPhotos)}
            locale={locale}
          />
        </div>
      </div>

    </div>
  );
}
