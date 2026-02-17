import { Routes, Route } from 'react-router-dom'
import GrapeVarietyPage from './pages/GrapeVarietyPage'
import WinegrowerPage from './pages/WinegrowerPage'
import MapPage from './pages/MapPage'
import TreePage from './pages/TreePage'
import Header from './components/Header'

// Mock data for Acadie Blanc
const mockVariety = {
  name: "Acadie Blanc",
  aliases: ["L'Acadie Blanc", "V 53261"],
  vivc_number: "17638",
  slug: "acadie-blanc",
  
  // Photos (using actual files)
  photos: [
    "vivc_17638_Cluster_in_the_field_17107k.jpg",
    "vivc_17638_Mature_leaf_12774k.jpg"
  ],
  
  // Basic info
  summary: "White cold-climate hybrid from Canada, best known as Nova Scotia's signature white and cornerstone of Tidal Bay blends.",
  year_of_crossing: 1953,
  breeder: "O.A. Bradt at Vineland Research Station",
  parents: ["Cascade", "Seyve-Villard 14-287"],
  species: "Vitis Interspecific Crossing",
  country_of_origin: "Canada",
  known_for: "Nova Scotia's signature white variety",
  
  // Quick stats
  producer_count: 47,
  hardiness: "-25°C (-13°F)",
  wine_styles: ["Still", "Sparkling", "Tidal Bay"],
  ripening_season: "Mid-Late Season",
  
  // Related data
  top_regions: ["Nova Scotia", "Vermont", "Ontario"],
  research_sections: ["Overview", "Origin & Breeding", "Climate Adaptation", "Viticulture", "Winemaking"],
  citation_count: 40,
  
  // Related varieties
  similar_varieties: ["Seyval Blanc", "Vidal", "Geisenheim 318"],
  parent_crosses: ["Other Cascade crosses", "Other SV 14-287 crosses"]
}

// Mock data for Domaine des Feux Follets
const mockProducer = {
  name: "DOMAINE DES FEUX FOLLETS",
  business_name: "DOMAINE DES FEUX FOLLETS",
  permit_holder: "DOMAINE DES FEUX FOLLETS INC.",
  slug: "domaine-des-feux-follets",
  
  // Location
  address: "82, BOULEVARD BLAIS EST",
  city: "BERTHIER-SUR-MER",
  state_province: "Quebec",
  country: "CA",
  postal_code: "G0R1E0",
  latitude: 46.9287884,
  longitude: -70.722742,
  
  // Contact & Links
  website: "https://www.domainefeuxfollets.com",
  social_media: [
    "https://www.facebook.com/domainefeuxfollets",
    "https://www.instagram.com/domainefeuxfollets/"
  ],
  
  // Classification
  verified_wine_producer: true,
  permit_categories: ["ASRA", "LIQR", "MISR", "VIN"],
  open_for_visits: true,
  
  // Grape varieties (extracted from wines)
  grape_varieties: [
    "Radisson",
    "Frontenac Gris", 
    "Frontenac Blanc",
    "Acadie Blanc",
    "Somerset",
    "La Crescent",
    "Adalmiina",
    "Petite Pearl",
    "Marquette"
  ],
  
  // Wine types
  wine_types: ["White", "Red", "Rosé", "Sparkling", "Orange"],
  
  // Activities
  activities: ["Wine Production", "Organic Certified", "Natural Wines", "Tastings"],
  
  // Wines (sample from the data)
  wines: [
    {
      name: "L'ÉCHOUAGE 2023",
      description: "Rosé aux notes de fraise, bel équilibre entre fruit et acidité; vin léger et de plaisir, à déguster lors des beaux jours.",
      type: "Rosé",
      vintage: "2023",
      cepages: ["Radisson"]
    },
    {
      name: "COUP DE NORDET 2023", 
      description: "Vin blanc vif et citronné, notes de fruit frais et sésame grillé légèrement fumé; accords fruits de mer (huîtres, ceviche).",
      type: "White",
      vintage: "2023",
      cepages: ["Adalmiina", "Frontenac Blanc"]
    },
    {
      name: "CLAYVER COSMIQUE 2023",
      description: "Vin rouge de soif, sec et fruité avec arômes de fruits rouges et cerise, notes poivrées; tanins souples; servi frais (10–13°C).",
      type: "Red", 
      vintage: "2023",
      cepages: ["Petite Pearl"]
    },
    {
      name: "LE CHANT DE LA SIRÈNE 2024",
      description: "Vin blanc pétillant, notes de poire et fleurs d'arbres fruitiers; bulle versatile pour apéritif ou desserts (tarte tatin, fromages).",
      type: "Sparkling",
      vintage: "2024", 
      cepages: ["Acadie Blanc", "Frontenac Blanc"]
    },
    {
      name: "ORANGE MÉLODIQUE 2023",
      description: "Vin orange aromatique et sec; arômes de bergamote, clémentine, abricot, notes florales et légère amertume; belle longueur.",
      type: "Orange",
      vintage: "2023",
      cepages: ["Frontenac Blanc", "Adalmiina", "La Crescent"]
    }
  ]
}

function App() {
  return (
    <div className="app">
      <Routes>
        <Route path="/" element={
          <div className="landing-page">
            <div className="landing-container">
              <div className="landing-header">
                <h1 className="landing-title">🍇 Grape Geek</h1>
                <p className="landing-subtitle">Discover cold-climate grape varieties</p>
              </div>
              
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Search grape varieties..."
                  className="search-box"
                />
              </div>
              
              <div className="landing-footer">
                <p>Explore the world of cold-hardy grape varieties</p>
              </div>
            </div>
          </div>
        } />
        <Route path="/variety/:slug" element={
          <>
            <Header showBackLink={true} />
            <GrapeVarietyPage variety={mockVariety} />
          </>
        } />
        <Route path="/variety/:slug/tree" element={<TreePage />} />
        <Route path="/tree" element={<TreePage />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/variety/:slug/map" element={<MapPage />} />
        <Route path="/variety/:slug/research" element={
          <>
            <Header showBackLink={true} />
            <div>Research view coming soon...</div>
          </>
        } />
        <Route path="/winegrower/:slug" element={
          <>
            <Header showBackLink={true} />
            <WinegrowerPage producer={mockProducer} />
          </>
        } />
        <Route path="*" element={
          <>
            <Header showBackLink={true} />
            <GrapeVarietyPage variety={mockVariety} />
          </>
        } />
      </Routes>
    </div>
  )
}

export default App