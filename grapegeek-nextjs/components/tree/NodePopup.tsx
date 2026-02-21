import React from 'react';
import Link from 'next/link';

interface NodeData {
  label: string;
  vivc_number?: string | number;
  species?: string;
  berry_color?: string;
  country?: string;
  sex?: string;
  year_crossing?: string | number;
  breeder?: string;
  speciesComposition?: Array<{ species: string; proportion: number }>;
  has_producers?: boolean;
}

interface NodePopupProps {
  node: { data: NodeData } | null;
  isVisible: boolean;
  onClose: () => void;
  position: { x: number; y: number };
}

const NodePopup: React.FC<NodePopupProps> = ({ node, isVisible, onClose, position }) => {
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
    speciesComposition
  } = node.data;

  const getSexSymbol = (sex: string) => {
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

  const getBerryEmoji = (berryColor: string) => {
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
          border: '2px solid #667eea',
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
        {/* Title with link to variety page */}
        <div style={{
          fontWeight: 'bold',
          marginBottom: '12px',
          fontSize: '16px',
          borderBottom: '1px solid #e9ecef',
          paddingBottom: '8px'
        }}>
          <Link
            href={`/varieties/${encodeURIComponent(label)}`}
            style={{
              color: '#667eea',
              textDecoration: 'none'
            }}
            onMouseOver={(e) => (e.currentTarget.style.textDecoration = 'underline')}
            onMouseOut={(e) => (e.currentTarget.style.textDecoration = 'none')}
          >
            {label}
          </Link>
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
                  color: '#667eea',
                  textDecoration: 'none',
                  borderBottom: '1px dotted #667eea'
                }}
                onMouseOver={(e) => (e.currentTarget.style.textDecoration = 'underline')}
                onMouseOut={(e) => (e.currentTarget.style.textDecoration = 'none')}
              >
                {vivc_number}
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

        {/* View Full Profile Link */}
        <div style={{
          marginTop: '12px',
          paddingTop: '8px',
          borderTop: '1px solid #e9ecef'
        }}>
          <Link
            href={`/varieties/${encodeURIComponent(label)}`}
            style={{
              fontSize: '14px',
              color: '#667eea',
              fontWeight: 500,
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
            onMouseOver={(e) => (e.currentTarget.style.color = '#5a67d8')}
            onMouseOut={(e) => (e.currentTarget.style.color = '#667eea')}
          >
            View Full Profile →
          </Link>
        </div>
      </div>
    </>
  );
};

export default NodePopup;
