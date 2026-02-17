# Design System & UI Guidelines

## Design Philosophy

Grape Geek follows a **magazine-style editorial design** that emphasizes beautiful photography, scannable content, and intuitive navigation. The design balances scientific precision with visual appeal to make grape variety research accessible and engaging.

## Core Principles

### 1. **Photography-First**
- Grape cluster photos are the hero element of each variety page
- Portrait-oriented layout optimized for grape cluster photography
- High-quality imagery takes precedence over text in visual hierarchy

### 2. **Scannable Content**
- Information is organized in digestible, visual chunks
- Preview sections provide quick overviews with "dive deeper" options
- Accordion-style research allows users to explore specific topics

### 3. **Progressive Disclosure**
- Start with overview, allow drilling down into details
- Static previews launch into full interactive experiences
- Sticky navigation provides constant access to different sections

### 4. **Modern Editorial Layout**
- Magazine-inspired typography and spacing
- Generous white space for breathing room
- Clean lines and subtle shadows for depth

## Visual Identity

### Color Palette

#### Primary Colors
```css
--primary-blue: #007bff     /* Primary actions, links, active states */
--success-green: #28a745    /* Nova Scotia markers, success states */
--warning-yellow: #ffc107   /* Vermont markers, attention elements */
```

#### Text Colors
```css
--text-primary: #212529     /* Headlines, important text */
--text-secondary: #495057   /* Body text, descriptions */
--text-muted: #6c757d       /* Supporting text, labels */
```

#### Background Colors
```css
--bg-primary: #ffffff       /* Cards, content areas */
--bg-secondary: #f8f9fa     /* Alternate sections, subtle backgrounds */
--bg-tertiary: #e9ecef      /* Borders, dividers */
```

#### Semantic Colors
```css
--error: #dc3545          /* Error states */
--warning: #ffc107        /* Warning states */
--info: #17a2b8          /* Information */
--success: #28a745       /* Success states */
```

### Color Usage Guidelines

#### **Geographic Color Coding**
- **Nova Scotia**: Green (`#28a745`) - Primary growing region
- **Vermont**: Yellow (`#ffc107`) - Secondary region
- **Ontario**: Blue (`#007bff`) - Tertiary region
- **Other**: Various blues and teals for additional regions

#### **Interactive States**
- **Default**: Muted colors (`#6c757d`)
- **Hover**: Primary blue (`#007bff`)
- **Active**: Darker primary (`#0056b3`)
- **Disabled**: Light gray (`#e9ecef`)

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
             'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
             sans-serif;
```

**Rationale**: System fonts provide optimal performance and native feel across platforms.

### Type Scale

#### **Display Typography**
```css
.variety-title {
  font-size: 3rem;        /* 48px */
  font-weight: 300;       /* Light */
  line-height: 1.1;
}

.section-heading {
  font-size: 2.5rem;      /* 40px */
  font-weight: 300;       /* Light */
  line-height: 1.2;
}

.variety-tagline {
  font-size: 1.3rem;      /* 20.8px */
  font-weight: 400;       /* Regular */
  line-height: 1.5;
}
```

#### **Body Typography**
```css
.body-large {
  font-size: 1.1rem;      /* 17.6px */
  line-height: 1.6;
}

.body-regular {
  font-size: 1rem;        /* 16px */
  line-height: 1.6;
}

.body-small {
  font-size: 0.9rem;      /* 14.4px */
  line-height: 1.5;
}

.caption {
  font-size: 0.8rem;      /* 12.8px */
  line-height: 1.4;
}
```

### Typography Guidelines

#### **Hierarchy**
1. **Page Title** (3rem): Main variety name
2. **Section Headings** (2.5rem): "Where It Grows", "Family Tree", etc.
3. **Tagline** (1.3rem): Variety description/summary
4. **Body Text** (1rem): Main content, details
5. **Labels** (0.9rem): Form labels, metadata
6. **Captions** (0.8rem): Photo credits, fine print

#### **Weight Usage**
- **300 (Light)**: Large headings, elegant feel
- **400 (Regular)**: Body text, descriptions
- **500 (Medium)**: Labels, button text
- **600 (Semi-bold)**: Emphasis, important details
- **700 (Bold)**: Strong emphasis, call-to-action

## Spacing System

### Base Unit: `1rem` (16px)

#### **Spacing Scale**
```css
--space-xs: 0.25rem;    /* 4px  - tight spacing */
--space-sm: 0.5rem;     /* 8px  - small gaps */
--space-md: 1rem;       /* 16px - default spacing */
--space-lg: 1.5rem;     /* 24px - comfortable spacing */
--space-xl: 2rem;       /* 32px - generous spacing */
--space-2xl: 3rem;      /* 48px - section separation */
--space-3xl: 4rem;      /* 64px - major section padding */
```

#### **Layout Spacing**
```css
/* Section padding */
.section {
  padding: 4rem 2rem;     /* Generous vertical, comfortable horizontal */
}

/* Content max-width */
.content {
  max-width: 1200px;      /* Optimal reading width */
  margin: 0 auto;
}

/* Component gaps */
.hero-grid {
  gap: 3rem;              /* Substantial gap between photo and info */
}

.preview-content {
  gap: 4rem;              /* Large gap for landscape preview sections */
}
```

## Component Specifications

### Hero Section

#### **Layout**
```css
.hero-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 3rem 2rem;
}

.hero-grid {
  display: grid;
  grid-template-columns: 500px 1fr;  /* Fixed photo width, flexible info */
  gap: 3rem;
  align-items: start;
}
```

#### **Photo Specifications**
- **Dimensions**: 500px × 600px container
- **Aspect Ratio**: Portrait orientation preferred
- **Format**: JPG optimized for web
- **Quality**: High resolution for detailed grape clusters
- **Hover**: Subtle scale effect (1.02x)

### Section Navigation

#### **Behavior**
- **Sticky**: Remains visible when scrolling
- **Active States**: Underline + color change for current section
- **Smooth Scroll**: Animated scroll to sections with offset for sticky header

#### **Styling**
```css
.section-nav {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-button.active {
  color: #007bff;
  border-bottom: 3px solid #007bff;
  background: rgba(0,123,255,0.05);
}
```

### Preview Sections

#### **Map Preview**
```css
.map-rectangle {
  width: 100%;
  height: 400px;
  background: linear-gradient(135deg, #e8f4fd 0%, #d4f1f4 100%);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
```

#### **Tree Preview**
```css
.tree-mockup {
  min-height: 300px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1.5rem;
}

.node-content {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1rem 1.5rem;
}
```

### Interactive Elements

#### **Buttons**
```css
/* Primary Button */
.launch-button {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(0,123,255,0.3);
  transition: all 0.2s ease;
}

.launch-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,123,255,0.4);
}
```

#### **Accordion**
```css
.accordion-header {
  padding: 1.5rem 2rem;
  transition: background 0.2s;
  cursor: pointer;
}

.accordion-header:hover {
  background: #f8f9fa;
}

.accordion-content {
  padding: 0 2rem 2rem 2rem;
  animation: slideDown 0.2s ease;
}
```

## Responsive Design

### Breakpoints
```css
/* Mobile First Approach */
/* Small devices (phones) */
@media (max-width: 576px) { }

/* Medium devices (tablets) */
@media (max-width: 768px) { }

/* Large devices (desktops) */
@media (min-width: 769px) { }

/* Extra large devices */
@media (min-width: 1200px) { }
```

### Responsive Behavior

#### **Hero Section**
- **Desktop**: Side-by-side photo and info
- **Mobile**: Stacked layout, photo above info
- **Photo Size**: Maintains aspect ratio, scales to container

#### **Preview Sections**
- **Desktop**: Landscape layout (visual + details side-by-side)
- **Mobile**: Stacked layout (visual above details)
- **Navigation**: Horizontal scroll on mobile, full width on desktop

#### **Typography**
- **Desktop**: Full type scale
- **Mobile**: Reduced scale (3rem → 2rem for main title)

## Animation & Motion

### Principles
- **Subtle**: Enhance usability without distraction
- **Fast**: 200-300ms duration for most interactions
- **Eased**: Natural easing curves (ease, ease-in-out)
- **Purposeful**: Every animation serves a functional purpose

### Animation Catalog

#### **Hover Effects**
```css
/* Photo hover */
.main-photo:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}

/* Button hover */
.launch-button:hover {
  transform: translateY(-2px);
  transition: all 0.2s ease;
}

/* Map hover */
.map-background:hover {
  transform: scale(1.02);
  transition: transform 0.2s ease;
}
```

#### **State Transitions**
```css
/* Accordion open/close */
.accordion-content {
  animation: slideDown 0.2s ease;
}

/* Navigation active states */
.nav-button {
  transition: all 0.2s ease;
}

/* Section scroll */
scroll-behavior: smooth;
```

## Accessibility Guidelines

### Color Contrast
- **AA Compliance**: Minimum 4.5:1 contrast ratio for normal text
- **AAA Compliance**: 7:1 contrast ratio for important elements
- **Color Independence**: Information never conveyed by color alone

### Interactive Elements
- **Touch Targets**: Minimum 44px × 44px for mobile
- **Focus Indicators**: Clear focus rings for keyboard navigation
- **Semantic HTML**: Proper heading hierarchy, landmarks, lists

### Screen Reader Support
```html
<!-- ARIA labels for complex interactions -->
<button aria-label="Open interactive map">
<nav aria-label="Section navigation">
<section aria-labelledby="map-heading">

<!-- Screen reader only content -->
<span class="sr-only">Additional context for screen readers</span>
```

## Component Library

### Status Legend
- ✅ **Complete**: Fully implemented and styled
- 🚧 **In Progress**: Partially implemented
- 📋 **Planned**: Designed but not implemented

### Components

#### ✅ Layout Components
- **Header**: Site navigation with back links
- **SectionNav**: Sticky section navigation with scroll tracking
- **Hero**: Title, tagline, photo, and info layout

#### ✅ Content Components
- **GrapePhotos**: Portrait-optimized photo gallery
- **GrapeInfo**: Variety details and statistics
- **MapPreview**: Static map with click invitation
- **TreePreview**: Family tree genealogy preview
- **ResearchAccordion**: Collapsible research sections

#### 📋 Planned Components
- **VarietyCard**: Grid item for variety browsing
- **SearchBox**: Variety search and filtering
- **PhotoLightbox**: Full-screen photo viewing
- **InteractiveMap**: Full Leaflet map implementation
- **InteractiveTree**: Full React Flow tree implementation

## Brand Guidelines

### Voice & Tone
- **Authoritative**: Backed by research and citations
- **Accessible**: Complex topics explained clearly
- **Enthusiastic**: Passionate about grape varieties
- **Respectful**: Acknowledges uncertainty and conflicting sources

### Content Guidelines
- **Headings**: Sentence case preferred
- **Numbers**: Spell out numbers one through nine, use numerals for 10+
- **Citations**: Include source attribution for all claims
- **Measurements**: Use metric with imperial in parentheses where relevant

### Photography Standards
- **Subject**: Focus on grape clusters in their natural environment
- **Orientation**: Portrait preferred for main variety photos
- **Quality**: High resolution, sharp focus, good lighting
- **Context**: Include leaves and vineyard context when possible
- **Consistency**: Similar lighting and composition across varieties

## Performance Guidelines

### CSS Performance
- **Vanilla CSS**: No runtime CSS-in-JS overhead
- **Critical CSS**: Above-the-fold styles inlined
- **Unused CSS**: Removed in production builds
- **CSS Grid/Flexbox**: Modern layout methods for better performance

### Image Performance
- **Optimized**: Compressed for web without quality loss
- **Lazy Loading**: Load images as they enter viewport
- **Responsive Images**: Multiple sizes for different screen densities
- **WebP Support**: Modern format with JPG fallbacks

### Animation Performance
- **Transform/Opacity**: Use GPU-accelerated properties
- **will-change**: Sparingly used for complex animations
- **requestAnimationFrame**: For JavaScript animations
- **Reduced Motion**: Respect user preferences for motion