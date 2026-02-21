import { getDatabase } from '@/lib/database';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';
import GrapePhotos from '@/components/variety/GrapePhotos';
import GrapeInfo from '@/components/variety/GrapeInfoNew';
import MapPreview from '@/components/variety/MapPreview';
import TreePreviewReactFlow from '@/components/variety/TreePreviewReactFlow';
import ResearchAccordion from '@/components/variety/ResearchAccordion';
import SectionNav from '@/components/variety/SectionNav';
import DataDisclaimer from '@/components/variety/DataDisclaimer';
import ProductionStats from '@/components/variety/ProductionStats';

// Static generation: pre-render all variety pages at build time
export async function generateStaticParams() {
  const db = getDatabase();
  const names = db.getAllVarietyNames();

  return names.map((name) => ({
    name: encodeURIComponent(name),
  }));
}

// Generate metadata for SEO
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const db = getDatabase();
  const varietyName = decodeURIComponent(params.name);
  const variety = db.getVariety(varietyName, true);

  if (!variety) {
    return {
      title: 'Variety Not Found | GrapeGeek',
      description: 'The requested grape variety could not be found.'
    };
  }

  const usageCount = variety.uses?.length || 0;
  const description = [
    variety.name,
    variety.species ? `is a ${variety.species} grape variety` : 'grape variety',
    variety.berry_skin_color ? `with ${variety.berry_skin_color} berries` : '',
    usageCount > 0 ? `Used by ${usageCount} winegrower${usageCount !== 1 ? 's' : ''} in North America.` : ''
  ].filter(Boolean).join(' ');

  return {
    title: `${variety.name} - Grape Variety | GrapeGeek`,
    description: description,
  };
}

interface Props {
  params: { name: string };
}

export default function VarietyDetailPage({ params }: Props) {
  const db = getDatabase();
  const varietyName = decodeURIComponent(params.name);
  const variety = db.getVariety(varietyName, true);

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
              {variety.species && `${variety.species} grape variety`}
              {variety.berry_skin_color && ` with ${variety.berry_skin_color} berries`}
            </p>
          </div>

          <div className="variety-hero-grid">
            {hasPhotos ? (
              <GrapePhotos variety={variety} />
            ) : (
              <div className="grape-photos grape-photos-missing">
                <div className="missing-photo-container">
                  <div className="missing-photo-icon">🍇</div>
                  <div className="missing-photo-text">
                    <h3>No Photo Available</h3>
                    <p>Photo for this variety is not yet in our collection</p>
                  </div>
                </div>
              </div>
            )}
            <GrapeInfo variety={variety} />
          </div>
        </div>
      </section>

      {/* Sticky Section Navigation */}
      <SectionNav hasPhotos={hasPhotos} />

      {/* Map and Tree Adaptive Layout */}
      <div className="adaptive-previews-container">
        {/* Map Preview Section */}
        <section id="map" className="section-preview adaptive-preview">
          <div className="section-content">
            <MapPreview variety={variety} />
          </div>
        </section>

        {/* Family Tree Preview Section */}
        <section id="tree" className="section-preview adaptive-preview">
          <div className="section-content">
            <TreePreviewReactFlow variety={variety} />
          </div>
        </section>
      </div>

      {/* Production Statistics Section */}
      <section id="production" className="section-production">
        <div className="section-content">
          <ProductionStats
            varietyName={variety.name}
            stats={productionStats}
          />
        </div>
      </section>

      {/* Research Section */}
      <section id="research" className="section-research">
        <div className="section-content">
          <ResearchAccordion variety={variety} />
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
                  <strong>Photo Credits:</strong> {photoType} - {credits}
                  {photo.vivc_url && (
                    <>
                      {' '}Source:{' '}
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
