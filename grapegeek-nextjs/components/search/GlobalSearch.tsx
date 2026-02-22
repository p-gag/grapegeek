'use client';

import { useState, useRef, useEffect, useMemo, useCallback, useId } from 'react';
import { useRouter } from 'next/navigation';
import Fuse from 'fuse.js';
import { MapPin, Search, X } from 'lucide-react';
import type { SearchItem, SearchVarietyItem, SearchWinegrowerItem } from '@/lib/types';
import { slugify } from '@/lib/utils';

export type { SearchItem };

// ─── Color helpers ────────────────────────────────────────────────────────────

const COLOR_PATTERNS: [RegExp, string][] = [
  [/black|blue/i, '#3D1F6E'],
  [/dark.red|noir/i, '#7D1B2B'],
  [/red/i, '#C0392B'],
  [/pink|rosé|rose/i, '#D4608A'],
  [/grey|gray/i, '#8A8AA8'],
  [/white|green/i, '#9BB87A'],
];

function berryColor(color?: string): string {
  if (!color) return '#A89CC8';
  for (const [re, hex] of COLOR_PATTERNS) if (re.test(color)) return hex;
  return '#A89CC8';
}

function berryLabel(color?: string): string {
  if (!color) return '';
  if (/black|blue/i.test(color)) return 'Dark';
  if (/red/i.test(color)) return 'Red';
  if (/pink|rosé|rose/i.test(color)) return 'Rosé';
  if (/grey|gray/i.test(color)) return 'Grey';
  if (/white|green/i.test(color)) return 'White';
  return '';
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function GrapeClusterIcon({ color }: { color: string }) {
  return (
    <svg viewBox="0 0 22 26" className="w-5 h-5 flex-shrink-0" aria-hidden>
      <circle cx="11" cy="4"  r="3.2" fill={color} />
      <circle cx="6"  cy="9"  r="3.2" fill={color} />
      <circle cx="16" cy="9"  r="3.2" fill={color} />
      <circle cx="8"  cy="15" r="3.2" fill={color} />
      <circle cx="14" cy="15" r="3.2" fill={color} />
      <circle cx="11" cy="21" r="3.2" fill={color} />
      <line x1="11" y1="0" x2="11" y2="4" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function VarietyRow({ item, active, label }: { item: SearchVarietyItem; active: boolean; label: string }) {
  const bc = berryColor(item.color);
  const bl = berryLabel(item.color);
  return (
    <div className={`flex items-center gap-3 px-4 py-2.5 transition-colors border-l-2 ${active ? 'bg-brand/20 border-brand' : 'border-transparent hover:bg-gray-50'}`}>
      <span className="flex items-center justify-center w-8 h-8 rounded-full flex-shrink-0" style={{ background: bc + '22' }}>
        <GrapeClusterIcon color={bc} />
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
        {item.country && <p className="text-xs text-gray-400 truncate">{item.country}</p>}
      </div>
      <div className="flex items-center gap-1.5 flex-shrink-0">
        {bl && (
          <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full font-medium" style={{ background: bc + '22', color: bc }}>
            <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ background: bc }} />
            {bl}
          </span>
        )}
        <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-brand/10 text-brand">{label}</span>
      </div>
    </div>
  );
}

function WinegrowerRow({ item, active, label }: { item: SearchWinegrowerItem; active: boolean; label: string }) {
  const location = [item.city, item.state].filter(Boolean).join(', ');
  return (
    <div className={`flex items-center gap-3 px-4 py-2.5 transition-colors border-l-2 ${active ? 'bg-brand/20 border-brand' : 'border-transparent hover:bg-gray-50'}`}>
      <span className="flex items-center justify-center w-8 h-8 rounded-full bg-sky-50 flex-shrink-0">
        <MapPin className="w-4 h-4 text-sky-500" />
      </span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">{item.name}</p>
        {location && <p className="text-xs text-gray-400 truncate">{location}</p>}
      </div>
      <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-sky-100 text-sky-600 flex-shrink-0">{label}</span>
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

interface GlobalSearchProps {
  items: SearchItem[];
  locale: string;
  placeholder?: string;
  labelVariety?: string;
  labelWinegrower?: string;
}

const FUSE_OPTIONS = {
  threshold: 0.35,
  includeScore: true,
  ignoreLocation: true,
  minMatchCharLength: 2,
  keys: [
    { name: 'name',    weight: 3 },
    { name: 'aliases', weight: 2 },
    { name: 'city',    weight: 0.6 },
    { name: 'state',   weight: 0.4 },
    { name: 'country', weight: 0.3 },
  ],
};

const MAX_RESULTS = 8;

export default function GlobalSearch({ items, locale, placeholder = 'Search varieties & winegrowers…', labelVariety = 'Variety', labelWinegrower = 'Winegrower' }: GlobalSearchProps) {
  const router      = useRouter();
  const uid         = useId();                          // stable IDs for ARIA
  const listboxId   = `${uid}-listbox`;
  const optionId    = (i: number) => `${uid}-option-${i}`;

  const [query, setQuery]   = useState('');
  const [open, setOpen]     = useState(false);
  const [cursor, setCursor] = useState(-1);

  const inputRef     = useRef<HTMLInputElement>(null);

  // ── Auto-focus on mount ──────────────────────────────────────────────────
  useEffect(() => { inputRef.current?.focus(); }, []);
  const containerRef = useRef<HTMLDivElement>(null);
  const activeRef    = useRef<HTMLLIElement>(null);

  const fuse = useMemo(() => new Fuse(items, FUSE_OPTIONS), [items]);

  const results = useMemo<SearchItem[]>(() => {
    if (query.trim().length < 2) return [];
    return fuse.search(query).slice(0, MAX_RESULTS).map(r => r.item);
  }, [fuse, query]);

  const showDropdown = open && results.length > 0;

  // ── Global ⌘K / Ctrl+K shortcut ─────────────────────────────────────────
  useEffect(() => {
    function handle(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        inputRef.current?.select();
      }
    }
    document.addEventListener('keydown', handle);
    return () => document.removeEventListener('keydown', handle);
  }, []);

  // ── Close on outside click ───────────────────────────────────────────────
  useEffect(() => {
    function handle(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, []);

  // ── Auto-select first result when results change ─────────────────────────
  useEffect(() => { setCursor(results.length > 0 ? 0 : -1); }, [results]);

  // ── Scroll active item into view ─────────────────────────────────────────
  useEffect(() => {
    if (cursor >= 0 && activeRef.current) {
      activeRef.current.scrollIntoView({ block: 'nearest' });
    }
  }, [cursor]);

  // ── Navigation ───────────────────────────────────────────────────────────
  const navigate = useCallback((item: SearchItem) => {
    const href = item.type === 'variety'
      ? `/${locale}/varieties/${slugify(item.name)}`
      : `/${locale}/winegrowers/${item.slug}`;
    router.push(href);
    setQuery('');
    setOpen(false);
    inputRef.current?.blur();
  }, [router, locale]);

  // ── Keyboard handler ──────────────────────────────────────────────────────
  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        if (!showDropdown) { setOpen(true); break; }
        setCursor(c => (c + 1) % results.length);
        break;

      case 'ArrowUp':
        e.preventDefault();
        setCursor(c => c <= 0 ? results.length - 1 : c - 1);
        break;

      case 'Enter':
        if (cursor >= 0 && results[cursor]) {
          e.preventDefault();
          navigate(results[cursor]);
        }
        break;

      case 'Tab':
        // Close naturally — focus moves to next element
        setOpen(false);
        break;

      case 'Escape':
        if (showDropdown) {
          e.preventDefault();        // don't blur
          setOpen(false);
          setCursor(-1);
        } else if (query) {
          e.preventDefault();
          setQuery('');
        }
        break;
    }
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-2xl mx-auto">
      {/* ── Input ──────────────────────────────────────────────────────── */}
      <div className={`flex items-center gap-3 bg-white/95 backdrop-blur-sm rounded-2xl px-5 py-4 shadow-2xl transition-all ring-2 ${open ? 'ring-brand/40' : 'ring-white/60'}`}>
        <Search className="w-5 h-5 text-gray-400 flex-shrink-0" aria-hidden />

        <input
          ref={inputRef}
          type="text"
          value={query}
          placeholder={placeholder}
          className="flex-1 bg-transparent text-gray-900 placeholder-gray-400 text-base outline-none"
          onChange={e => { setQuery(e.target.value); setOpen(true); }}
          onFocus={() => { if (results.length > 0) setOpen(true); }}
          onKeyDown={onKeyDown}
          autoComplete="off"
          spellCheck={false}
          /* ARIA combobox pattern */
          role="combobox"
          aria-expanded={showDropdown}
          aria-haspopup="listbox"
          aria-autocomplete="list"
          aria-controls={listboxId}
          aria-activedescendant={cursor >= 0 ? optionId(cursor) : undefined}
        />

        {/* Shortcut hint */}
        {!query && (
          <kbd className="hidden sm:inline-flex items-center gap-1 text-xs text-gray-300 font-mono border border-gray-200 rounded px-1.5 py-0.5 flex-shrink-0">
            <span className="text-[10px]">⌘</span>K
          </kbd>
        )}

        {/* Clear button */}
        {query && (
          <button
            onClick={() => { setQuery(''); setOpen(false); inputRef.current?.focus(); }}
            className="text-gray-400 hover:text-gray-600 transition-colors flex-shrink-0"
            aria-label="Clear search"
            tabIndex={-1}           // keyboard users use Escape instead
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* ── Dropdown ───────────────────────────────────────────────────── */}
      {showDropdown && (
        <div className="absolute top-full mt-2 left-0 right-0 bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden z-50">
          <ul
            id={listboxId}
            role="listbox"
            aria-label="Search results"
            className="max-h-[360px] overflow-y-auto overscroll-contain"
          >
            {results.map((item, i) => {
              const id   = item.type === 'variety' ? item.name : item.slug;
              const isActive = cursor === i;
              return (
                <li
                  key={id}
                  id={optionId(i)}
                  role="option"
                  aria-selected={isActive}
                  ref={isActive ? activeRef : null}
                >
                  {/* mousedown prevents blur on input before click fires */}
                  <button
                    className="w-full text-left"
                    tabIndex={-1}
                    onMouseDown={e => { e.preventDefault(); navigate(item); }}
                    onMouseEnter={() => setCursor(i)}
                  >
                    {item.type === 'variety'
                      ? <VarietyRow item={item} active={isActive} label={labelVariety} />
                      : <WinegrowerRow item={item} active={isActive} label={labelWinegrower} />
                    }
                  </button>
                </li>
              );
            })}
          </ul>

          {/* Footer */}
          <div className="px-4 py-2.5 border-t border-gray-100 bg-gray-50/60">
            <p className="text-xs text-gray-400">
              <kbd className="font-mono">↑↓</kbd> navigate &nbsp;
              <kbd className="font-mono">↵</kbd> open &nbsp;
              <kbd className="font-mono">Esc</kbd> close
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
