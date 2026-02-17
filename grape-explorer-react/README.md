# 🍇 Grape Geek

A modern web application for exploring cold-climate grape varieties with beautiful photography, family trees, producer maps, and comprehensive research.

**This is a prototype of the incoming new Grape Geek site that will replace the current MkDocs site in the future.**

## ✨ Features

- **Beautiful variety profiles** with portrait grape cluster photography
- **Interactive family trees** showing grape genealogy and parentage
- **Producer maps** discovering wineries across North America
- **Research content** with comprehensive technical analysis
- **Magazine-style design** with smooth scrolling navigation
- **Mobile responsive** design that works on all devices
- **Modern Purple Design System** - Clean, data-centric knowledge platform aesthetic

## 🚀 Quick Start

```bash
# Install and run
npm install
npm run dev
```

Open http://localhost:3000

## 🏗️ Architecture

### Components
- **GrapeVarietyPage** - Main scrollable page with hero, previews, research
- **GrapePhotos** - Portrait-optimized photo gallery
- **MapPreview/TreePreview** - Static previews that launch full experiences
- **ResearchAccordion** - Collapsible technical sections
- **SectionNav** - Sticky navigation with scroll tracking

### Data Flow
Currently uses mock data for Acadie Blanc. Future versions will load variety data from JSON files and launch full interactive components.

## 🎨 Design

**Magazine-style storytelling** approach:
- Large hero photos with variety information
- Scannable preview sections for map/tree/research
- Smooth navigation between content areas
- Portrait photo optimization for grape clusters

**Modern Purple Design System**:
- Brand colors: Deep violet (#3D3553), Purple accent (#6B46C1)
- Background: Soft purple-gray (#F5F6FA)
- Typography: Clean, modern sans-serif with generous spacing
- Shadows: Subtle, modern elevation system
- Layout: CSS Grid responsive, 1200px max-width

## 🎯 Status

**Completed**: Hero section, navigation, map/tree previews, research accordion, responsive design, modern purple design system

**Next**: Dynamic data loading, full interactive map/tree components, variety hub page, migration of MkDocs content

## 🔧 Development

```bash
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview production
```

**Adding varieties**: Add photos to `/public/photos/`, create data objects
**Styling**: Global CSS in `src/index.css` with comprehensive CSS variables system
**Browser support**: Modern browsers, mobile-first responsive

## 🔮 Future

This React application is designed to replace the current MkDocs-based Grape Geek site, offering a more modern, interactive, and visually engaging user experience for exploring grape varieties, producers, and research content.
