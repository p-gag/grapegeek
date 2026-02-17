# Technical Design Document

## Architecture Overview

Grape Geek is built as a modern React single-page application (SPA) with a component-based architecture designed for scalability, maintainability, and performance.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Browser                                  │
├─────────────────────────────────────────────────────────────────┤
│                    React Application                            │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Routing     │  │  Components  │  │    State Management  │  │
│  │ React Router  │  │   Library    │  │      React Hooks     │  │
│  └───────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Build System                               │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │     Vite      │  │     ESLint   │  │     Hot Reload       │  │
│  │ Dev Server    │  │   Linting    │  │   Development        │  │
│  └───────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                     Static Assets                               │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │    Photos     │  │  JSON Data   │  │       Fonts          │  │
│  │  /public/     │  │   Files      │  │    System Fonts      │  │
│  └───────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Component Hierarchy

```
App (Router)
└── GrapeVarietyPage
    ├── Header (Global)
    ├── Hero Section
    │   ├── GrapePhotos
    │   └── GrapeInfo
    ├── SectionNav (Sticky)
    ├── MapPreview
    ├── TreePreview
    └── ResearchAccordion
```

### Component Responsibilities

#### **Core Page Components**
- **`App.jsx`**: Root component with routing logic and global state
- **`GrapeVarietyPage.jsx`**: Main variety page container, coordinates all sections
- **`Header.jsx`**: Global navigation with back links and search

#### **Content Components**
- **`GrapePhotos.jsx`**: Photo gallery optimized for portrait grape clusters
- **`GrapeInfo.jsx`**: Variety details, stats, and breeding information
- **`MapPreview.jsx`**: Static map preview with click-to-open functionality
- **`TreePreview.jsx`**: Family tree preview with genealogy visualization
- **`ResearchAccordion.jsx`**: Collapsible research sections with citations

#### **Navigation Components**
- **`SectionNav.jsx`**: Sticky section navigation with scroll tracking
- **`TabNavigation.jsx`**: Legacy tab system (deprecated)
- **`TabContent.jsx`**: Legacy content switching (deprecated)

## Data Architecture

### Current Data Flow

```
Mock Data Object (App.jsx)
        ↓
   GrapeVarietyPage
        ↓
  Component Props
        ↓
   Render UI
```

### Planned Data Flow

```
JSON Files (/public/data/)
        ↓
   Fetch API Calls
        ↓
   React State (useState/useEffect)
        ↓
   Component Props
        ↓
   Render UI
```

### Data Models

#### **Variety Object Schema**
```typescript
interface GrapeVariety {
  // Identity
  name: string;
  slug: string;
  aliases: string[];
  vivc_number: string;
  
  // Media
  photos: string[];
  hero_photo?: string;
  
  // Basic Info
  summary: string;
  country_of_origin: string;
  year_of_crossing: number;
  breeder: string;
  species: string;
  known_for: string;
  
  // Stats
  producer_count: number;
  hardiness: string;
  wine_styles: string[];
  ripening_season: string;
  
  // Relationships
  parents: string[];
  siblings?: string[];
  similar_varieties: string[];
  
  // Geographic
  top_regions: string[];
  
  // Research
  research_sections: ResearchSection[];
  citation_count: number;
}

interface ResearchSection {
  id: string;
  title: string;
  icon: string;
  content: string;
  citations?: Citation[];
}
```

## State Management

### Current Approach: Local State
- **Component State**: `useState` for simple local state
- **Props Drilling**: Data passed through component props
- **Event Handlers**: Callback functions for user interactions

### State Examples
```javascript
// Section navigation active tracking
const [activeSection, setActiveSection] = useState('overview');

// Research accordion open/closed state
const [openSections, setOpenSections] = useState(['overview']);

// Photo gallery selection
const [selectedPhoto, setSelectedPhoto] = useState(0);
```

### Future: Context API
For complex state that needs to be shared across many components:

```javascript
// Variety context for global variety data
const VarietyContext = createContext();

// Search/filter context for variety discovery
const SearchContext = createContext();

// User preferences (theme, favorites, etc.)
const PreferencesContext = createContext();
```

## Styling Architecture

### CSS Organization

```
src/index.css
├── Global Resets & Base Styles
├── Typography System
├── Color System
├── Layout Components
│   ├── Header Styles
│   ├── Hero Section
│   ├── Section Navigation
│   └── Content Sections
├── Interactive Components
│   ├── Map Preview
│   ├── Tree Preview
│   ├── Research Accordion
│   └── Photo Gallery
├── Utility Classes
└── Responsive Breakpoints
```

### Design System Implementation

#### **CSS Custom Properties**
```css
:root {
  /* Colors */
  --primary-blue: #007bff;
  --success-green: #28a745;
  --warning-yellow: #ffc107;
  --text-primary: #212529;
  --text-secondary: #495057;
  --text-muted: #6c757d;
  
  /* Spacing */
  --section-padding: 4rem 2rem;
  --content-gap: 3rem;
  --element-gap: 1rem;
  
  /* Borders & Shadows */
  --border-radius: 12px;
  --card-shadow: 0 8px 32px rgba(0,0,0,0.1);
  --hover-shadow: 0 12px 40px rgba(0,0,0,0.15);
}
```

#### **Responsive Design Strategy**
```css
/* Mobile-first approach */
.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

/* Desktop enhancement */
@media (min-width: 768px) {
  .hero-grid {
    grid-template-columns: 500px 1fr;
    gap: 3rem;
  }
}
```

## Performance Considerations

### Current Optimizations
1. **Vite Build System**: Fast dev server and optimized production builds
2. **Image Optimization**: Portrait-optimized grape photos
3. **CSS Performance**: Vanilla CSS, no runtime CSS-in-JS overhead
4. **Component Lazy Loading**: Ready for React.lazy() implementation

### Planned Optimizations
1. **Code Splitting**: Route-based code splitting for full-screen components
2. **Image Lazy Loading**: Progressive image loading for photo galleries
3. **Data Caching**: Browser caching for variety JSON data
4. **Service Worker**: Offline support for core functionality

### Bundle Analysis
```bash
# Current bundle (estimated)
- React + React DOM: ~45kb (gzipped)
- React Router: ~12kb (gzipped)
- Application Code: ~25kb (gzipped)
- CSS: ~15kb (gzipped)
Total: ~97kb (gzipped)
```

## Security Considerations

### Current Security Measures
1. **No Server**: Static site deployment, no server vulnerabilities
2. **Content Security**: All content from trusted sources
3. **XSS Prevention**: React's built-in XSS protection
4. **No User Data**: No user authentication or data storage

### Future Security Requirements
1. **API Security**: HTTPS-only API calls when integrated
2. **Input Sanitization**: For search and filter inputs
3. **CSP Headers**: Content Security Policy for production deployment
4. **OWASP Guidelines**: Follow web application security best practices

## Testing Strategy

### Current Testing
- **Manual Testing**: Cross-browser and device testing
- **Development Testing**: Hot reload for immediate feedback
- **Accessibility**: Basic ARIA labels and semantic HTML

### Planned Testing
```javascript
// Unit Tests (Jest + React Testing Library)
describe('GrapePhotos', () => {
  test('displays variety photos correctly', () => {
    render(<GrapePhotos variety={mockVariety} />);
    expect(screen.getByAltText(/Acadie Blanc/)).toBeInTheDocument();
  });
});

// Integration Tests
describe('GrapeVarietyPage', () => {
  test('navigates between sections', async () => {
    render(<GrapeVarietyPage variety={mockVariety} />);
    fireEvent.click(screen.getByText('Family Tree'));
    await waitFor(() => {
      expect(screen.getByText('Explore the genealogy')).toBeInTheDocument();
    });
  });
});

// E2E Tests (Cypress)
describe('Variety Exploration', () => {
  it('should navigate through variety sections', () => {
    cy.visit('/variety/acadie-blanc');
    cy.get('[data-testid="map-preview"]').click();
    cy.url().should('include', '/variety/acadie-blanc/map');
  });
});
```

## Deployment Architecture

### Current Deployment
```
Development (localhost:3000)
        ↓
   npm run build
        ↓
   Static Files (dist/)
        ↓
   Static Hosting (Vercel/Netlify)
```

### Production Requirements
1. **CDN**: Content delivery network for global performance
2. **Compression**: Gzip/Brotli compression for assets
3. **Caching**: Browser caching headers for static assets
4. **HTTPS**: SSL/TLS encryption for all connections
5. **Monitoring**: Error tracking and performance monitoring

## Scalability Considerations

### Current Scalability
- **Static Assets**: Can handle high traffic with CDN
- **No Database**: No database bottlenecks
- **Client-Side Rendering**: Scales with CDN performance

### Future Scalability Challenges
1. **Data Volume**: Hundreds of grape varieties with photos and research
2. **Search Performance**: Client-side search with large datasets
3. **Interactive Components**: React Flow performance with large family trees
4. **Mobile Performance**: Large datasets on mobile devices

### Solutions
1. **Virtual Scrolling**: For large variety lists
2. **Data Pagination**: Load varieties on-demand
3. **Search Indexing**: Pre-computed search indices
4. **Progressive Web App**: Service workers for offline functionality

## Technology Choices Rationale

### React
- **Why**: Component-based architecture, large ecosystem, team familiarity
- **Alternatives Considered**: Vue.js, Svelte
- **Trade-offs**: Bundle size vs. development speed and ecosystem

### Vite
- **Why**: Fast development server, optimized builds, ES modules
- **Alternatives Considered**: Create React App, Webpack
- **Trade-offs**: Newer tool vs. proven reliability

### Vanilla CSS
- **Why**: No runtime overhead, full control, no learning curve
- **Alternatives Considered**: Styled Components, Tailwind CSS, Sass
- **Trade-offs**: Verbosity vs. performance and simplicity

### File-based Data
- **Why**: Simple deployment, no backend complexity, version control
- **Alternatives Considered**: Headless CMS, GraphQL API, Database
- **Trade-offs**: Static updates vs. dynamic content management