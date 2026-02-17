import { useNavigate, useLocation } from 'react-router-dom'

const Header = ({ showBackLink = false }) => {
  const navigate = useNavigate()
  const location = useLocation()

  const handleBackClick = () => {
    // If we're on a map page with a variety, go back to that variety
    if (location.pathname === '/map' && location.search.includes('variety=')) {
      const varietyParam = new URLSearchParams(location.search).get('variety')
      if (varietyParam) {
        const varietySlug = varietyParam.toLowerCase().replace(/\s+/g, '-')
        navigate(`/variety/${varietySlug}`)
        return
      }
    }
    
    // If we're on a tree page with a variety, go back to that variety
    if (location.pathname === '/tree' && location.search.includes('variety=')) {
      const varietyParam = new URLSearchParams(location.search).get('variety')
      if (varietyParam) {
        const varietySlug = varietyParam.toLowerCase().replace(/\s+/g, '-')
        navigate(`/variety/${varietySlug}`)
        return
      }
    }
    
    // Default: go back in history or to home
    if (window.history.length > 1) {
      navigate(-1)
    } else {
      navigate('/')
    }
  }

  return (
    <header className="header">
      <div className="header-left">
        {showBackLink && (
          <button 
            onClick={handleBackClick}
            className="header-back-link"
            style={{ background: 'none', border: 'none', cursor: 'pointer' }}
          >
            ← Back
          </button>
        )}
      </div>
      <h1 className="header-title">🍇 Grape Geek</h1>
      <input 
        type="text" 
        placeholder="Search varieties..." 
        className="search-box"
      />
    </header>
  )
}

export default Header