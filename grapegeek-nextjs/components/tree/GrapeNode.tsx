import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';
import { simplifySpeciesName } from '@/lib/utils';

// Species color constants
const SPECIES_COLORS: { [key: string]: string } = {
  'vinifera': '#90EE90',  // Light green - European wine grapes
  'riparia': '#87CEEB',   // Sky blue - Cold-hardy native
  'labrusca': '#BA55D3',  // Medium orchid
  'rupestris': '#FFA07A', // Light salmon - Rock grapes
  'aestivalis': '#FFFF00', // Yellow - Summer grapes
  'amurensis': '#FF1493', // Deep pink - Asian cold-hardy
  'rotundifolia': '#9370DB', // Medium slate blue - Muscadine grapes
  'unknown': '#999999'    // Gray - Unknown/unspecified
};

interface GrapeNodeProps {
  data: {
    label: string;
    country?: string;
    country_code?: string;
    sex?: string;
    is_selected?: boolean;
    is_duplicate?: boolean;
    is_hovered?: boolean;
    nodeBackgroundColor?: string;
    species?: string;
    berry_color?: string;
    colorMode?: string;
    speciesComposition?: Array<{ species: string; proportion: number }>;
    vivc_number?: string;
    year_crossing?: string;
    breeder?: string;
  };
  isConnectable: boolean;
}

const GrapeNode = memo(({ data, isConnectable }: GrapeNodeProps) => {
  const {
    label,
    country,
    country_code,
    sex,
    is_selected,
    is_duplicate,
    is_hovered,
    nodeBackgroundColor,
    species,
    berry_color,
    colorMode,
    speciesComposition = []
  } = data;

  // Function to break long titles into multiple lines
  const formatLabel = (text: string) => {
    if (!text) return text;

    const words = text.split(' ');
    if (words.length <= 1 || text.length <= 20) return text;

    // If it's a long single word, let CSS handle it
    if (words.length === 1) return text;

    // For multiple words, try to split at reasonable points
    const midPoint = Math.ceil(words.length / 2);
    const firstLine = words.slice(0, midPoint).join(' ');
    const secondLine = words.slice(midPoint).join(' ');

    // Prefer breaking at common patterns
    const breakPoints = [' D\'', ' DE ', ' DU ', ' DES ', ' LA ', ' LE ', ' LES '];
    for (const breakPoint of breakPoints) {
      const index = text.indexOf(breakPoint);
      if (index > 5 && index < text.length - 5) {
        return (
          <>
            {text.substring(0, index)}
            <br />
            {text.substring(index + 1)}
          </>
        );
      }
    }

    // Fallback to midpoint split
    if (firstLine.length <= 15 && secondLine.length <= 15) {
      return (
        <>
          {firstLine}
          <br />
          {secondLine}
        </>
      );
    }

    return text;
  };

  const getSexSymbol = (sex?: string) => {
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

  // Create tooltip content for detailed info
  const createTooltip = () => {
    const details = [];
    if (data.vivc_number) details.push(`VIVC: ${data.vivc_number}`);
    if (data.species) details.push(`Species: ${simplifySpeciesName(data.species)}`);
    if (data.berry_color) details.push(`Berry: ${data.berry_color}`);
    if (data.country) details.push(`Origin: ${data.country}`);
    if (data.year_crossing) details.push(`Year: ${data.year_crossing}`);
    if (data.breeder) details.push(`Breeder: ${data.breeder}`);
    return details.join('\n');
  };

  // Get species color
  const getSpeciesColor = (species?: string) => {
    if (!species) return SPECIES_COLORS['unknown'];

    const speciesLower = species.toLowerCase();
    if (speciesLower.includes('vinifera')) return SPECIES_COLORS['vinifera'];
    if (speciesLower.includes('riparia')) return SPECIES_COLORS['riparia'];
    if (speciesLower.includes('labrusca')) return SPECIES_COLORS['labrusca'];
    if (speciesLower.includes('rupestris')) return SPECIES_COLORS['rupestris'];
    if (speciesLower.includes('aestivalis') || speciesLower.includes('lincecumii')) return SPECIES_COLORS['aestivalis'];
    if (speciesLower.includes('amurensis')) return SPECIES_COLORS['amurensis'];
    if (speciesLower.includes('rotundifolia') || speciesLower.includes('muscadinia')) return SPECIES_COLORS['rotundifolia'];
    return SPECIES_COLORS['unknown'];
  };

  // Get berry color background
  const getBerryColor = (berryColor?: string) => {
    if (!berryColor) return 'rgba(248, 249, 250, 0.85)';

    const colorLower = berryColor.toLowerCase();
    if (colorLower.includes('blanc') || colorLower.includes('white')) {
      return 'rgba(240, 248, 255, 0.85)';
    } else if (colorLower.includes('rouge') || colorLower.includes('red') ||
               colorLower.includes('noir') || colorLower.includes('black')) {
      return 'rgba(255, 228, 225, 0.85)';
    } else if (colorLower.includes('rose') || colorLower.includes('pink')) {
      return 'rgba(255, 238, 240, 0.85)';
    } else if (colorLower.includes('gris') || colorLower.includes('gray')) {
      return 'rgba(245, 245, 245, 0.85)';
    } else {
      return 'rgba(248, 249, 250, 0.85)';
    }
  };

  // Create proportional species color bar
  const createSpeciesBar = () => {
    if (colorMode !== 'species') return null;

    // Use species composition data if available
    if (speciesComposition.length > 0) {
      return (
        <div style={{
          width: '100%',
          height: '10px',
          marginTop: '4px',
          borderRadius: '4px',
          border: '1px solid rgba(0,0,0,0.1)',
          display: 'flex',
          overflow: 'hidden'
        }}>
          {speciesComposition.map(({ species: speciesName, proportion }, index) => (
            <div
              key={index}
              style={{
                backgroundColor: getSpeciesColor(speciesName),
                width: `${proportion * 100}%`,
                height: '100%'
              }}
              title={`${speciesName}: ${(proportion * 100).toFixed(1)}%`}
            />
          ))}
        </div>
      );
    }

    // Fallback to own species as single color
    const fallbackSpecies = species || 'unknown';
    return (
      <div style={{
        width: '100%',
        height: '10px',
        marginTop: '4px',
        borderRadius: '4px',
        border: '1px solid rgba(0,0,0,0.1)',
        backgroundColor: getSpeciesColor(fallbackSpecies)
      }} />
    );
  };

  // Get node background color
  const getNodeBackgroundColor = () => {
    if (colorMode === 'species') {
      return 'white'; // Keep nodes white when showing species bars
    } else {
      return getBerryColor(berry_color);
    }
  };

  return (
    <div
      className={`grape-node compact ${is_selected ? 'selected' : ''} ${is_duplicate ? 'duplicate' : ''}`}
      title={createTooltip()}
      style={{
        backgroundColor: is_hovered
          ? 'rgba(0, 123, 255, 0.1)'
          : getNodeBackgroundColor(),
        borderColor: is_hovered ? '#0056b3' : (is_selected ? '#007bff' : '#bbb'),
        borderWidth: is_hovered ? '4px' : '3px',
        boxShadow: is_hovered
          ? '0 8px 24px rgba(0, 123, 255, 0.6), 0 0 0 2px rgba(0, 123, 255, 0.2)'
          : '0 1px 3px rgba(0,0,0,0.1)',
        transform: is_hovered ? 'scale(1.05)' : 'scale(1)',
        transition: 'all 0.2s ease',
        zIndex: is_hovered ? 1000 : 1
      }}
    >
      <Handle
        type="source"
        position={Position.Left}
        isConnectable={isConnectable}
      />

      <div className="grape-node-content">
        <div className="grape-name-line">
          {country_code && (
            <span className={`fi fi-${country_code}`} title={country}></span>
          )}
          <span className="grape-name">
            {formatLabel(label)}
            {sex && (
              <span className="sex-symbol" title={sex}>
                {' '}{getSexSymbol(sex)}
              </span>
            )}
          </span>
        </div>
      </div>

      {/* Species color bar */}
      {createSpeciesBar()}

      <Handle
        type="target"
        position={Position.Right}
        isConnectable={isConnectable}
      />
    </div>
  );
});

GrapeNode.displayName = 'GrapeNode';

export default GrapeNode;
