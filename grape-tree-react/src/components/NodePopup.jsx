import React from 'react';

const NodePopup = ({ node, isVisible, onClose, position }) => {
  if (!isVisible || !node) return null;

  const {
    label,
    vivc_number,
    species,
    berry_color,
    country,
    sex,
    year_crossing,
    breeder,
    speciesComposition,
    has_producers
  } = node.data;

  const getSexSymbol = (sex) => {
    if (!sex) return '';
    const sexLower = sex.toLowerCase();
    if (sexLower.includes('male') && !sexLower.includes('female')) {
      return '♂';
    } else if (sexLower.includes('female')) {
      return '♀';
    } else if (sexLower.includes('hermaphrodite')) {
      return '⚥';
    }
    return '❓';
  };

  const getBerryEmoji = (berryColor) => {
    if (!berryColor) return '🍇';
    
    const colorLower = berryColor.toLowerCase();
    if (colorLower.includes('blanc') || colorLower.includes('white')) {
      return '⚪';
    } else if (colorLower.includes('rouge') || colorLower.includes('red') || 
               colorLower.includes('noir') || colorLower.includes('black')) {
      return '🔴';
    } else if (colorLower.includes('rose') || colorLower.includes('pink')) {
      return '🌸';
    } else if (colorLower.includes('gris') || colorLower.includes('gray')) {
      return '⚫';
    } else {
      return '🍇';
    }
  };

  // Calculate species percentages for display
  const speciesPercentages = speciesComposition?.map(({ species, proportion }) => 
    `${species}: ${(proportion * 100).toFixed(1)}%`
  ).join(', ') || '';

  return (
    <>
      {/* Backdrop */}
      <div 
        className="popup-backdrop"
        onClick={onClose}
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          zIndex: 1000
        }}
      />
      
      {/* Popup */}
      <div 
        className="node-popup"
        style={{
          position: 'fixed',
          left: Math.min(position.x + 10, window.innerWidth - 320),
          top: Math.min(position.y - 10, window.innerHeight - 200),
          backgroundColor: 'rgba(255, 255, 255, 0.98)',
          border: '2px solid #007bff',
          borderRadius: '8px',
          padding: '16px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          zIndex: 1001,
          minWidth: '300px',
          maxWidth: '400px',
          fontSize: '14px',
          lineHeight: '1.4'
        }}
      >
        {/* Title */}
        <div style={{ 
          fontWeight: 'bold', 
          marginBottom: '12px', 
          color: '#007bff', 
          fontSize: '16px',
          borderBottom: '1px solid #e9ecef',
          paddingBottom: '8px'
        }}>
          {label}
        </div>
        
        {/* Content */}
        <div>
          {vivc_number && (
            <div style={{ marginBottom: '6px' }}>
              <strong>VIVC:</strong>{' '}
              <a 
                href={`https://www.vivc.de/index.php?r=passport%2Fview&id=${vivc_number}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#007bff',
                  textDecoration: 'none',
                  borderBottom: '1px dotted #007bff'
                }}
                onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                onMouseOut={(e) => e.target.style.textDecoration = 'none'}
              >
                {vivc_number}
              </a>
            </div>
          )}
          
          {/* Where It Grows link - only show if producers are available */}
          {has_producers && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Where It Grows:</strong>{' '}
              <a 
                href={`https://grapegeek.com/producer-map/?grape_variety=${encodeURIComponent(label)}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  color: '#007bff',
                  textDecoration: 'none',
                  borderBottom: '1px dotted #007bff'
                }}
                onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                onMouseOut={(e) => e.target.style.textDecoration = 'none'}
              >
                Producer Map 🗺️
              </a>
            </div>
          )}
          
          {species && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Species:</strong> {species}
            </div>
          )}
          
          {speciesPercentages && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Composition:</strong> {speciesPercentages}
            </div>
          )}
          
          {berry_color && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Berry:</strong> {getBerryEmoji(berry_color)} {berry_color}
            </div>
          )}
          
          {country && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Origin:</strong> {country}
            </div>
          )}
          
          {sex && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Sex:</strong> {getSexSymbol(sex)} {sex}
            </div>
          )}
          
          {year_crossing && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Year:</strong> {year_crossing}
            </div>
          )}
          
          {breeder && (
            <div style={{ marginBottom: '6px' }}>
              <strong>Breeder:</strong> {breeder}
            </div>
          )}
        </div>
        
        {/* Instructions */}
        <div style={{ 
          marginTop: '12px', 
          paddingTop: '8px',
          borderTop: '1px solid #e9ecef',
          color: '#666', 
          fontSize: '12px',
          fontStyle: 'italic'
        }}>
          Double-click to explore this variety's tree
        </div>
      </div>
    </>
  );
};

export default NodePopup;