import { useState } from 'react'

const GrapePhotos = ({ variety, photos }) => {
  const [isFullScreen, setIsFullScreen] = useState(false)

  // Only show the cluster photo
  const clusterPhoto = photos.find(photo => photo.includes('Cluster')) || photos[0]

  // Mock photo credits data (will come from grape_variety_mapping.json later)
  const photoCredits = "Ursula Brühl, Julius Kühn-Institut (JKI), Federal Research Centre for Cultivated Plants, Institute for Grapevine Breeding Geilweilerhof - 76833 Siebeldingen, GERMANY"

  const handleViewFullSize = () => {
    setIsFullScreen(true)
  }

  const handleCloseFullScreen = () => {
    setIsFullScreen(false)
  }

  return (
    <>
      <div className="grape-photos">
        {/* Main Photo Display */}
        <div className="main-photo-container">
          <img
            src={`/photos/${clusterPhoto}`}
            alt={`${variety.name} - Cluster in field`}
            className="main-photo"
          />

          {/* Photo Type Label */}
          <div className="photo-type-badge">
            Cluster in field
          </div>

          {/* Photo Credit */}
          <a
            href="#photo-credits"
            className="photo-credit-link"
            title={photoCredits}
          >
            Photo credit
          </a>

          {/* Expand button */}
          <button className="expand-btn" onClick={handleViewFullSize}>
            🔍 View Full Size
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
            <img
              src={`/photos/${clusterPhoto}`}
              alt={`${variety.name} - Cluster in field (Full size)`}
              className="photo-fullscreen"
              onClick={(e) => e.stopPropagation()}
            />
            <div className="photo-fullscreen-info">
              <div className="photo-fullscreen-credits">
                Photo: {photoCredits}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default GrapePhotos
