/**
 * Utility functions for GrapeGeek Next.js application
 */

/**
 * Format a date string
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

/**
 * Slugify a string for URLs
 */
export function slugify(text: string): string {
  return text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // strip accent diacritics (é→e, à→a, etc.)
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

/**
 * Format a variety name for display
 */
export function formatVarietyName(name: string): string {
  return name.trim();
}

/**
 * Get color for wine type
 */
export function getWineTypeColor(type: string): string {
  const typeColors: Record<string, string> = {
    'Red': 'bg-red-100 text-red-800',
    'White': 'bg-yellow-100 text-yellow-800',
    'Rosé': 'bg-pink-100 text-pink-800',
    'Sparkling': 'bg-blue-100 text-blue-800',
    'Dessert': 'bg-purple-100 text-purple-800',
    'Fortified': 'bg-orange-100 text-orange-800',
  };

  return typeColors[type] || 'bg-gray-100 text-gray-800';
}

/**
 * Simplify verbose botanical species names from VIVC.
 * e.g. "VITIS VINIFERA LINNÉ SUBSP. SATIVA (DE CANDOLLE) HEGI" → "Vitis vinifera"
 *      "VITIS INTERSPECIFIC CROSSING" → "Interspecific crossing"
 *      "MUSCADINIA ROTUNDIFOLIA MICHAUX VAR. ROTUNDIFOLIA" → "Muscadinia rotundifolia"
 */
export function simplifySpeciesName(species: string): string {
  if (!species) return species;

  const upper = species.toUpperCase().trim();

  // Handle crossing types
  if (upper.includes('INTERSPECIFIC CROSSING')) return 'Interspecific crossing';
  if (upper.includes('INTERGENERIC CROSSING')) return 'Intergeneric crossing';

  // Extract genus (first word) and species epithet (second word)
  const words = upper.split(/\s+/);
  if (words.length >= 2) {
    const genus = words[0].charAt(0) + words[0].slice(1).toLowerCase();
    const epithet = words[1].toLowerCase();
    return `${genus} ${epithet}`;
  }

  // Single word fallback
  return species.charAt(0).toUpperCase() + species.slice(1).toLowerCase();
}

/**
 * Get color for species
 */
export function getSpeciesColor(species: string): string {
  const speciesColors: Record<string, string> = {
    'Vitis vinifera': 'bg-purple-100 text-purple-800',
    'Hybrid': 'bg-green-100 text-green-800',
    'Vitis labrusca': 'bg-blue-100 text-blue-800',
    'Vitis riparia': 'bg-teal-100 text-teal-800',
  };

  return speciesColors[species] || 'bg-gray-100 text-gray-800';
}
