'use client';
import { useEffect } from 'react';

/** Locks body scroll for full-page views. Restores on unmount. */
export default function NoScroll() {
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    document.documentElement.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
      document.documentElement.style.overflow = '';
    };
  }, []);
  return null;
}
