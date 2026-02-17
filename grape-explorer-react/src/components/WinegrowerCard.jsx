const WinegrowerCard = ({ producer, selectedVariety = null }) => {
  const openWebsite = (url) => {
    if (url) {
      window.open(url, '_blank', 'noopener noreferrer')
    }
  }
  
  return (
    <div className="winegrower-card">
      {/* Header */}
      <div className="winegrower-header">
        <h3 className="winegrower-name">{producer.name}</h3>
        <div className="winegrower-location">
          <span className="location-icon">📍</span>
          {producer.city}, {producer.state_province}
        </div>
      </div>
      
      {/* Variety Pills */}
      {producer.grape_varieties && producer.grape_varieties.length > 0 && (
        <div className="winegrower-varieties">
          <div className="variety-pills">
            {producer.grape_varieties.map((variety, index) => (
              <span 
                key={`${variety}-${index}`}
                className={`variety-pill ${selectedVariety && variety === selectedVariety ? 'selected' : ''}`}
              >
                {variety}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Wine Types */}
      {producer.wine_types && producer.wine_types.length > 0 && (
        <div className="winegrower-wine-types">
          <div className="wine-types-text">
            <strong>Types:</strong> {producer.wine_types.join(', ')}
          </div>
        </div>
      )}
      
      {/* Bottom Section with Wine Count and Links */}
      <div className="winegrower-bottom">
        <div className="wine-count">
          {producer.wines ? `${producer.wines.length} wine${producer.wines.length !== 1 ? 's' : ''} found` : ''}
        </div>
        
        {(producer.website || (producer.social_media && producer.social_media.length > 0)) && (
          <div className="winegrower-actions">
            {producer.website && (
              <button 
                className="link-button website-link"
                onClick={() => openWebsite(producer.website)}
                title="Visit website"
              >
                <i className="fas fa-globe"></i>
              </button>
            )}
            
            {producer.social_media && producer.social_media.length > 0 && (
              <>
                {producer.social_media.map((social, index) => {
                  // Get platform-specific Font Awesome icon and color (matching original implementation)
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
                    if (urlLower.includes('linkedin.com')) {
                      return { icon: 'fab fa-linkedin', color: '#0A66C2', platform: 'LinkedIn' }
                    }
                    if (urlLower.includes('tiktok.com')) {
                      return { icon: 'fab fa-tiktok', color: '#000000', platform: 'TikTok' }
                    }
                    return { icon: 'fas fa-link', color: '#666', platform: 'Social Media' }
                  }
                  
                  const socialUrl = social.url || social
                  const { icon, color, platform } = getSocialIcon(socialUrl)
                  
                  return (
                    <button
                      key={index}
                      className="link-button social-link"
                      onClick={() => openWebsite(socialUrl)}
                      title={`Visit ${platform}`}
                      style={{ '--icon-color': color }}
                    >
                      <i className={icon}></i>
                    </button>
                  )
                })}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default WinegrowerCard