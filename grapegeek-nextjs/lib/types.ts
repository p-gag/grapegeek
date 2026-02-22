// Winegrower (previously Producer)
// Note: Database table is still "producers" but we use "winegrower" in UI
export interface Winegrower {
  id: number;
  permit_id: string;
  slug: string;  // URL-friendly version of business_name
  business_name: string;
  city: string;
  state_province: string;
  country: string;
  latitude?: number;
  longitude?: number;
  website?: string;
  wine_label?: string;
  permit_holder?: string;
  address?: string;
  postal_code?: string;
  classification?: string;
  verified_wine_producer: boolean;
  source?: string;
  geocoding_method?: string;
  enriched_at?: string;
  created_at?: string;
  wines?: Wine[];
  social_media?: string[];
  activities?: string[];
}

export interface Wine {
  id: number;
  winegrower_id: number;  // FK to producers table
  name: string;
  description?: string;
  winemaking?: string;
  type?: string;
  vintage?: string;
  grapes: WineGrape[];  // Grape composition with percentages
}

export interface WineGrape {
  variety_name: string;
  percentage?: number;
}

export interface GrapeVariety {
  id: number;
  name: string;
  is_grape: boolean;
  vivc_number?: number;
  berry_skin_color?: string;
  country_of_origin?: string;
  species?: string;
  parent1_name?: string;
  parent2_name?: string;
  breeder?: string;
  sex_of_flower?: string;
  year_of_crossing?: string;
  vivc_assignment_status?: string;
  no_wine: boolean;
  source?: string;
  aliases: string[];
  uses?: GrapeUse[];  // Which winegrowers use this variety
  photos?: GrapePhoto[];  // Photo data from VIVC or other sources
}

export interface GrapePhoto {
  id?: number;
  filename: string;
  type?: string;
  gcs_url?: string;
  vivc_url?: string;
  credits?: string;
}

export interface GrapeUse {
  wine_id: number;
  wine_name: string;
  winegrower_id: string;
  winegrower_name: string;
}

export interface MapMarker {
  permit_id: string;
  name: string;
  lat: number;
  lng: number;
  city: string;
  state_province: string;
  country: string;
  varieties: string[];
  wine_types: string[];
}

export interface DatabaseStats {
  total_winegrowers: number;
  total_varieties: number;
  total_wines: number;
  true_grapes: number;
  countries: { [country: string]: number };
  top_states_provinces: { [state: string]: number };
  species: { [species: string]: number };
  berry_colors: { [color: string]: number };
  geolocated_winegrowers: number;
  winegrowers_with_websites: number;
}

// Production statistics types
export interface VarietalStats {
  varietal_count: number;
  blended_count: number;
  total_wines: number;
  varietal_percentage: number;
}

export interface BlendPartner {
  variety_name: string;
  co_occurrence_count: number;
  percentage: number;
}

export interface PlantedNeighbor {
  variety_name: string;
  producer_count: number;
  percentage: number;
}

export interface ProducerUsage {
  producer_id: string;
  business_name: string;
  wines_with_variety: number;
  total_wines: number;
  usage_percentage: number;
  state_province: string;
  country: string;
}

export interface GeographicDistribution {
  state_province: string;
  country: string;
  producer_count: number;
  wine_count: number;
  percentage: number;
}

export interface VarietyProductionStats {
  varietal_stats: VarietalStats;
  common_blends: BlendPartner[];
  planted_neighbors: PlantedNeighbor[];
  top_producers: ProducerUsage[];
  geographic_distribution: GeographicDistribution[];
}

// ========================================
// Search types
// ========================================

export interface SearchVarietyItem {
  type: 'variety';
  name: string;
  color?: string;
  country?: string;
  aliases: string[];
}

export interface SearchWinegrowerItem {
  type: 'winegrower';
  name: string;
  slug: string;
  city?: string;
  state?: string;
  country?: string;
}

export type SearchItem = SearchVarietyItem | SearchWinegrowerItem;
