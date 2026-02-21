'use client';

import { useState, useEffect, useMemo } from 'react';

interface SectionNavProps {
  hasPhotos?: boolean;
}

export default function SectionNav({ hasPhotos = false }: SectionNavProps) {
  const [activeSection, setActiveSection] = useState('overview');

  const sections = useMemo(() => {
    return [
      { id: 'overview', label: 'Overview', icon: '🍇' },
      { id: 'map', label: 'Map', icon: '🗺️' },
      { id: 'tree', label: 'Family Tree', icon: '🌳' },
      { id: 'production', label: 'Production', icon: '📊' },
      { id: 'research', label: 'Research', icon: '📚' },
    ];
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const headerOffset = 120; // Account for sticky nav height
      const elementPosition = element.getBoundingClientRect().top;
      const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth',
      });
    }
  };

  // Track active section on scroll
  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + 200;

      for (let i = sections.length - 1; i >= 0; i--) {
        const element = document.getElementById(sections[i].id);
        if (element && element.offsetTop <= scrollPosition) {
          setActiveSection(sections[i].id);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sections]);

  return (
    <nav className="section-nav">
      <div className="nav-content">
        <div className="nav-buttons">
          {sections.map((section) => (
            <button
              key={section.id}
              className={`nav-button ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => scrollToSection(section.id)}
            >
              <span className="nav-icon">{section.icon}</span>
              <span className="nav-label">{section.label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}
