import WinegrowerMap from '../components/WinegrowerMap'
import WinegrowerVarieties from '../components/WinegrowerVarieties'
import DataDisclaimer from '../components/DataDisclaimer'

const WinegrowerPage = ({ producer }) => {
  const getDomainFavicon = (url) => {
    try {
      const domain = new URL(url).hostname
      return `https://www.google.com/s2/favicons?domain=${domain}&sz=32`
    } catch {
      return null
    }
  }

  return (
    <div className="winegrower-page">
      {/* Page Header */}
      <div className="winegrower-header">
        <h1 className="winegrower-title">{producer.name}</h1>
        <p className="winegrower-location">
          📍 {producer.city}, {producer.state_province}
          {producer.open_for_visits && <span className="visits-badge"> • Open for visits</span>}
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="winegrower-content-grid">
        {/* Left Column: Map + Contact */}
        <div className="winegrower-map-column">
          <WinegrowerMap producer={producer} />
          <div className="winegrower-contact-links">
            {producer.website && (
              <a
                href={producer.website}
                target="_blank"
                rel="noopener noreferrer"
                className="contact-link website-link"
              >
                {getDomainFavicon(producer.website) ? (
                  <img
                    src={getDomainFavicon(producer.website)}
                    alt="Website icon"
                    className="website-favicon"
                  />
                ) : (
                  <i className="fas fa-globe"></i>
                )}
                <span>Website</span>
              </a>
            )}

            {producer.social_media && producer.social_media.length > 0 && (
              producer.social_media.map((social, index) => {
                const getSocialIcon = (url) => {
                  const urlLower = (url || '').toLowerCase()

                  if (urlLower.includes('facebook.com')) {
                    return { icon: 'fab fa-facebook', color: '#1877F2', platform: 'Facebook' }
                  }
                  if (urlLower.includes('instagram.com')) {
                    return { icon: 'fab fa-instagram', color: '#E4405F', platform: 'Instagram' }
                  }
                  if (urlLower.includes('twitter.com') || urlLower.includes('x.com')) {
                    return { icon: 'fab fa-x-twitter', color: '#000000', platform: 'Twitter/X' }
                  }
                  if (urlLower.includes('youtube.com')) {
                    return { icon: 'fab fa-youtube', color: '#FF0000', platform: 'YouTube' }
                  }
                  return { icon: 'fas fa-link', color: '#666', platform: 'Social' }
                }

                const socialUrl = social.url || social
                const { icon, color, platform } = getSocialIcon(socialUrl)

                return (
                  <a
                    key={index}
                    href={socialUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="contact-link social-link"
                    title={platform}
                  >
                    <i className={icon} style={{ color }}></i>
                    <span>{platform}</span>
                  </a>
                )
              })
            )}
          </div>
        </div>

        {/* Right Column: Varieties */}
        <div className="winegrower-info-column">
          <WinegrowerVarieties producer={producer} />
        </div>
      </div>

      {/* Footer: Data Disclaimer */}
      <DataDisclaimer type="winegrower" />
    </div>
  )
}

export default WinegrowerPage