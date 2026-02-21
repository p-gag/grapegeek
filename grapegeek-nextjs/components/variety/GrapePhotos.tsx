'use client';

import { useState } from 'react';
import type { GrapeVariety } from '@/lib/types';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface GrapePhotosProps {
  variety: GrapeVariety;
  locale: Locale;
}

export default function GrapePhotos({ variety, locale }: GrapePhotosProps) {
  const t = createTranslator(locale);
  const [isFullScreen, setIsFullScreen] = useState(false);

  // Check if photos exist
  if (!variety.photos || variety.photos.length === 0) {
    return null; // Don't render if no photos
  }

  // Only show the cluster photo
  const clusterPhoto = variety.photos.find(photo =>
    photo.type?.toLowerCase().includes('cluster')
  ) || variety.photos[0];

  // Use GCS URL directly
  const photoUrl = clusterPhoto.gcs_url;

  // Photo credits - use from photo data or default
  const photoCredits = clusterPhoto.credits ||
    "Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY";

  const handleViewFullSize = () => {
    setIsFullScreen(true);
  };

  const handleCloseFullScreen = () => {
    setIsFullScreen(false);
  };

  const handlePhotoCreditsClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const creditsElement = document.querySelector('#photo-credits .credits-text');
    if (creditsElement) {
      // Scroll to element
      creditsElement.scrollIntoView({ behavior: 'smooth', block: 'center' });

      // Select the text after scrolling
      setTimeout(() => {
        const range = document.createRange();
        range.selectNodeContents(creditsElement);
        const selection = window.getSelection();
        selection?.removeAllRanges();
        selection?.addRange(range);
      }, 500);
    }
  };

  return (
    <>
      <div className="grape-photos">
        {/* Main Photo Display */}
        <div className="main-photo-container">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={photoUrl}
            alt={`${variety.name} - Cluster in field`}
            className="main-photo"
            crossOrigin="anonymous"
            onError={(e) => {
              // Fallback to placeholder if image doesn't exist
              const target = e.target as HTMLImageElement;
              target.src = 'https://via.placeholder.com/600x600/8B5CF6/FFFFFF?text=' + encodeURIComponent(variety.name);
            }}
          />

          {/* Photo Credit */}
          <a
            href="#photo-credits"
            className="photo-credit-link"
            title={photoCredits}
            onClick={handlePhotoCreditsClick}
          >
            {t('variety.photoCredit')}
          </a>

          {/* Expand button */}
          <button className="expand-btn" onClick={handleViewFullSize}>
            🔍 {t('variety.viewFullSize')}
          </button>
        </div>
      </div>

      {/* Full Screen Photo Modal */}
      {isFullScreen && (
        <div className="photo-fullscreen-overlay" onClick={handleCloseFullScreen}>
          <div className="photo-fullscreen-container">
            <button className="photo-close-btn" onClick={handleCloseFullScreen}>
              ✕
            </button>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={photoUrl}
              alt={`${variety.name} - Cluster in field (Full size)`}
              className="photo-fullscreen"
              crossOrigin="anonymous"
              onClick={(e) => e.stopPropagation()}
              onError={(e) => {
                // Fallback to placeholder if image doesn't exist
                const target = e.target as HTMLImageElement;
                target.src = 'https://via.placeholder.com/800x800/8B5CF6/FFFFFF?text=' + encodeURIComponent(variety.name);
              }}
            />
            <div className="photo-fullscreen-info">
              <div className="photo-fullscreen-credits">
                {t('variety.photoCredit')}: {photoCredits}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
