'use client';

import { useState, useEffect, useMemo } from 'react';
import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface SectionNavProps {
  hasPhotos?: boolean;
  locale: Locale;
}

export default function SectionNav({ hasPhotos = false, locale }: SectionNavProps) {
  const t = createTranslator(locale);
  const [activeSection, setActiveSection] = useState('overview');

  const sections = useMemo(() => {
    return [
      { id: 'overview', label: t('variety.sectionNav.overview'), icon: '🍇' },
      { id: 'map', label: t('variety.sectionNav.map'), icon: '🗺️' },
      { id: 'tree', label: t('variety.sectionNav.tree'), icon: '🌳' },
      { id: 'production', label: t('variety.sectionNav.production'), icon: '📊' },
      { id: 'research', label: t('variety.sectionNav.research'), icon: '📚' },
    ];
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [locale]);

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
