import { getDatabase } from '@/lib/database';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import GrapePhotos from '@/components/variety/GrapePhotos';
import GrapeInfo from '@/components/variety/GrapeInfoNew';
import MapPreview from '@/components/variety/MapPreview';
import TreePreviewReactFlow from '@/components/variety/TreePreviewReactFlow';
import ResearchAccordion from '@/components/variety/ResearchAccordion';
import SectionNav from '@/components/variety/SectionNav';
import ProductionStats from '@/components/variety/ProductionStats';
import { type Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';
import { slugify, simplifySpeciesName } from '@/lib/utils';

interface Props {
  params: { locale: Locale; name: string };
}

// Static generation: pre-render all variety pages at build time
export async function generateStaticParams() {
  const db = getDatabase();
  return db.getAllVarietySlugs().map((slug) => ({ name: slug }));
}

// Generate metadata for SEO
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const t = createTranslator(params.locale);
  const db = getDatabase();
  const variety = db.getVarietyBySlug(params.name, true);

  if (!variety) {
    return {
      title: `${t('variety.notFound.title')} | GrapeGeek`,
      description: t('variety.notFound.text'),
    };
  }

  const usageCount = variety.uses?.length || 0;
  const description = [
    variety.name,
    variety.species ? `is a ${simplifySpeciesName(variety.species)} ${t('variety.grapeVariety')}` : t('variety.grapeVariety'),
    variety.berry_skin_color ? t('variety.withBerries', { color: variety.berry_skin_color }) : '',
    usageCount > 0 ? `Used by ${usageCount} winegrower${usageCount !== 1 ? 's' : ''} in North America.` : ''
  ].filter(Boolean).join(' ');

  return {
    title: `${variety.name} - ${t('variety.grapeVariety')} | GrapeGeek`,
    description: description,
    alternates: {
      canonical: `https://grapegeek.com/${params.locale}/varieties/${params.name}`,
      languages: {
        en: `https://grapegeek.com/en/varieties/${params.name}`,
        fr: `https://grapegeek.com/fr/varieties/${params.name}`,
      },
    },
  };
}

export default function VarietyDetailPage({ params }: Props) {
  const { locale } = params;
  const t = createTranslator(locale);
  const db = getDatabase();
  const variety = db.getVarietyBySlug(params.name, true);

  if (!variety) {
    notFound();
  }

  const hasPhotos = variety.photos && variety.photos.length > 0;

  // Load production statistics
  const productionStats = db.getVarietyProductionStats(variety.name);

  return (
    <div className="grape-variety-page">
      {/* Hero Section with Photo and Info */}
      <section id="overview" className="variety-hero-section">
        <div className="variety-hero-content">
          <div className="variety-hero-header">
            <h1 className="variety-title">{variety.name}</h1>
            <p className="variety-tagline">
              {variety.species && `${simplifySpeciesName(variety.species)} ${t('variety.grapeVariety')}`}
              {variety.berry_skin_color && ` ${t('variety.withBerries', { color: variety.berry_skin_color })}`}
            </p>
          </div>

          <div className="variety-hero-grid">
            {hasPhotos ? (
              <GrapePhotos variety={variety} locale={locale} />
            ) : (
              <div className="grape-photos grape-photos-missing">
                <div className="missing-photo-container">
                  <div className="missing-photo-icon">🍇</div>
                  <div className="missing-photo-text">
                    <h3>{t('variety.noPhoto')}</h3>
                    <p>{t('variety.noPhotoText')}</p>
                  </div>
                </div>
              </div>
            )}
            <GrapeInfo variety={variety} locale={locale} productionStats={productionStats} />
          </div>
        </div>
      </section>

      {/* Sticky Section Navigation */}
      <SectionNav hasPhotos={hasPhotos} locale={locale} />

      {/* Map and Tree Adaptive Layout */}
      <div className="adaptive-previews-container">
        {/* Map Preview Section */}
        <section id="map" className="section-preview adaptive-preview">
          <div className="section-content">
            <MapPreview variety={variety} locale={locale} />
          </div>
        </section>

        {/* Family Tree Preview Section */}
        <section id="tree" className="section-preview adaptive-preview">
          <div className="section-content">
            <TreePreviewReactFlow variety={variety} locale={locale} />
          </div>
        </section>
      </div>

      {/* Production Statistics Section */}
      <section id="production" className="section-production">
        <div className="section-content">
          <ProductionStats
            varietyName={variety.name}
            stats={productionStats}
            locale={locale}
          />
        </div>
      </section>

      {/* Research Section */}
      <section id="research" className="section-research">
        <div className="section-content">
          <ResearchAccordion variety={variety} locale={locale} />
        </div>
      </section>

      {/* Photo Credits Section */}
      {hasPhotos && variety.photos && variety.photos.length > 0 && (
        <section id="photo-credits" className="photo-credits-section">
          <div className="section-content">
            {variety.photos.map((photo, index) => {
              const credits = photo.credits || 'Photo credits not available';
              const photoType = photo.type || 'Photograph';

              return (
                <p key={index} className="credits-text">
                  <strong>{t('variety.photoCredits')}</strong> {photoType} - {credits}
                  {photo.vivc_url && (
                    <>
                      {' '}{t('variety.source')}{' '}
                      <a href="http://www.vivc.de" target="_blank" rel="noopener noreferrer">
                        VIVC
                      </a>
                    </>
                  )}
                </p>
              );
            })}
          </div>
        </section>
      )}

    </div>
  );
}
