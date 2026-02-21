# TDD: Internationalization (i18n) for GrapeGeek Next.js

## Goal

Add French language support to the Next.js static site. English is the default language, French is a variation. The site must be SEO-friendly with separate URLs per language, proper `hreflang` tags, and a language switcher. A Python sync script auto-translates English strings to French using OpenAI, with per-entry hash-based change detection.

## Constraints

- **Static export only** (`output: 'export'` in next.config.js) — no runtime middleware, no server-side locale detection
- **Route paths always English** — `/fr/varieties/Marquette`, never `/fr/cepages/Marquette`
- **Variety names, winegrower names, wine names are proper nouns** — never translated, passed as interpolation variables
- **Database content stays English** — species, berry colors, cities, countries come from DB unchanged
- **~200 UI strings** across ~40 component files need extraction

## Architecture

### URL Structure

Both languages are prefixed. English is `x-default`.

```
/en/                          ← English homepage
/en/varieties                 ← English varieties list
/en/varieties/Marquette       ← English variety detail
/en/winegrowers/some-winery   ← English winegrower detail
/fr/                          ← French homepage
/fr/varieties                 ← French varieties list
/fr/varieties/Marquette       ← French variety detail (same slug)
/fr/winegrowers/some-winery   ← French winegrower detail (same slug)
```

Root `/` serves a static redirect page to `/en/`.

### Route Restructure

Move all pages under `app/[locale]/`. Keep `api/` outside.

**Before:**
```
app/
  page.tsx
  layout.tsx
  varieties/
    page.tsx
    [name]/page.tsx
  winegrowers/
    page.tsx
    [slug]/page.tsx
  map/page.tsx
  stats/page.tsx
  tree/page.tsx
  about/page.tsx
  api/map-data/route.ts
```

**After:**
```
app/
  page.tsx                    ← root redirect to /en/
  [locale]/
    layout.tsx                ← sets <html lang>, hreflang, loads messages
    page.tsx                  ← homepage
    varieties/
      page.tsx
      [name]/
        page.tsx
        not-found.tsx
    winegrowers/
      page.tsx
      [slug]/page.tsx
    map/
      page.tsx
      layout.tsx              ← existing no-header layout
    stats/page.tsx
    tree/page.tsx
    about/page.tsx
  api/map-data/route.ts       ← stays outside [locale]
```

### Locale Configuration

```typescript
// lib/i18n/config.ts
export const locales = ['en', 'fr'] as const;
export type Locale = (typeof locales)[number];
export const defaultLocale: Locale = 'en';
```

### Static Params Generation

Every `[locale]` layout/page must export `generateStaticParams` that returns both locales. For nested dynamic routes, params compose automatically.

```typescript
// app/[locale]/layout.tsx
export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

// app/[locale]/varieties/[name]/page.tsx
export async function generateStaticParams() {
  const db = getDatabase();
  const names = db.getAllVarietyNames();
  // Next.js composes with parent [locale] params automatically
  return names.map((name) => ({ name: encodeURIComponent(name) }));
}
```

## Translation System

### File Structure

```
messages/
  en.json              ← source of truth (flat key-value)
  fr.json              ← AI-translated values
  fr.hashes.json       ← SHA-256 hash of each English source value
```

### Message Format

Flat key-value with dot-notation namespacing. Variables use `{curly braces}`. Plurals use separate keys with `.zero`, `.one`, `.other` suffixes.

**`messages/en.json`:**
```json
{
  "nav.home": "GrapeGeek",
  "nav.varieties": "Varieties",
  "nav.winegrowers": "Winegrowers",
  "nav.map": "Map",
  "nav.stats": "Stats",
  "nav.about": "About",

  "home.hero.title": "GrapeGeek",
  "home.hero.subtitle": "Discover cold-climate grape varieties and the winegrowers who grow them",
  "home.hero.exploreMap": "Explore Map",
  "home.hero.browseVarieties": "Browse Varieties",
  "home.stats.title": "By the Numbers",
  "home.stats.varieties": "Grape Varieties",
  "home.stats.winegrowers": "Winegrowers",
  "home.stats.countries": "Countries",
  "home.stats.wines": "Wine Products",
  "home.features.title": "Explore Cold-Climate Viticulture",
  "home.features.map.title": "Interactive Map",
  "home.features.map.description": "Explore winegrowers across northeastern North America with filtering by variety and location.",
  "home.features.varieties.title": "Grape Varieties",
  "home.features.varieties.description": "Discover cold-hardy hybrid varieties, their parentage, and characteristics.",
  "home.features.stats.title": "Statistics",
  "home.features.stats.description": "Analyze trends in variety usage, winegrower distribution, and more.",

  "varieties.title": "Grape Varieties",
  "varieties.subtitle": "Browse {count} cold-climate grape varieties",
  "varieties.showing": "Showing {filtered} of {total} varieties",
  "varieties.noResults": "No varieties found matching your criteria.",
  "varieties.clearFilters": "Clear all filters",
  "varieties.filter.title": "Filter Varieties",
  "varieties.filter.clearAll": "Clear all",
  "varieties.filter.search": "Search varieties...",
  "varieties.filter.allSpecies": "All Species",
  "varieties.filter.allColors": "All Colors",
  "varieties.filter.trueGrapesOnly": "True grapes only ({count})",

  "variety.grapeVariety": "grape variety",
  "variety.withBerries": "with {color} berries",
  "variety.noPhoto": "No Photo Available",
  "variety.noPhotoText": "Photo for this variety is not yet in our collection",
  "variety.photoCredits": "Photo Credits:",
  "variety.source": "Source:",
  "variety.sectionNav.overview": "Overview",
  "variety.sectionNav.map": "Map",
  "variety.sectionNav.tree": "Family Tree",
  "variety.sectionNav.production": "Production",
  "variety.sectionNav.research": "Research",
  "variety.info.bred": "Bred",
  "variety.info.parents": "Parents",
  "variety.info.species": "Species",
  "variety.info.berryColor": "Berry Color",
  "variety.info.knownFor": "Known for",
  "variety.info.origin": "Origin",
  "variety.info.vivcNumber": "VIVC Number",
  "variety.info.quickStats": "Quick Stats",
  "variety.info.viewOnVivc": "View on VIVC",
  "variety.info.winegrowers": "North American Winegrowers",
  "variety.info.coldHardiness": "Cold Hardiness",
  "variety.info.wineStyles": "Wine Styles",
  "variety.info.ripeningSeasons": "Ripening Season",
  "variety.winegrowers.title": "Winegrowers Using This Variety",
  "variety.winegrowers.none": "No winegrowers found using {variety}",
  "variety.winegrowers.noneSubtext": "This variety may be newly planted or not yet tracked in our database.",
  "variety.winegrowers.count.one": "{count} winegrower growing {variety} in North America",
  "variety.winegrowers.count.other": "{count} winegrowers growing {variety} in North America",
  "variety.winegrowers.winesFeaturing": "Wines featuring {variety}:",
  "variety.winegrowers.viewDetails": "View Details",
  "variety.winegrowers.totalWines": "Total wines featuring {variety}: {count}",
  "variety.winegrowers.viewOnMap": "View on Map",

  "winegrowers.title": "Winegrowers",
  "winegrowers.subtitle": "Explore {count} winegrowers across northeastern North America",
  "winegrowers.showing": "Showing {filtered} of {total} winegrowers",
  "winegrowers.noResults": "No winegrowers found matching your criteria.",
  "winegrowers.clearFilters": "Clear Filters",
  "winegrowers.filter.title": "Filter Winegrowers",
  "winegrowers.filter.clearAll": "Clear all",
  "winegrowers.filter.search": "Search by name or city...",
  "winegrowers.filter.allCountries": "All Countries",
  "winegrowers.filter.allStates": "All States/Provinces",

  "_comment": "...continue for all ~200 strings (map, stats, tree, about, etc.)"
}
```

**Important — variable names in translated strings:**

Variables like `{variety}`, `{winegrower}`, `{count}` are **placeholders that the translator must preserve verbatim**. The sync script prompt must instruct the AI:
- Keep all `{variable}` placeholders exactly as-is
- Never translate the content inside `{}`
- Sentence structure may change around variables (French word order differs)

Example:
```json
// en: "Wines featuring {variety}:"
// fr: "Vins mettant en vedette {variety} :"
```

### Translation Lookup

**`lib/i18n/messages.ts`:**
```typescript
import en from '@/messages/en.json';
import fr from '@/messages/fr.json';
import { Locale } from './config';

const messages: Record<Locale, Record<string, string>> = { en, fr };

export function getMessages(locale: Locale): Record<string, string> {
  return messages[locale] ?? messages.en;
}
```

**`lib/i18n/translate.ts`:**
```typescript
import { Locale } from './config';
import { getMessages } from './messages';

type TranslateFunction = (key: string, params?: Record<string, string | number>) => string;

/**
 * Returns a translate function bound to a locale.
 * Handles variable interpolation and plural selection.
 *
 * Usage:
 *   const t = createTranslator('fr');
 *   t('variety.winegrowers.count', { count: 5, variety: 'Marquette' })
 *   // → "5 vignobles cultivant Marquette en Amérique du Nord"
 */
export function createTranslator(locale: Locale): TranslateFunction {
  const msgs = getMessages(locale);

  return (key: string, params?: Record<string, string | number>): string => {
    let resolved = key;

    // Plural resolution: if params.count exists, try .zero/.one/.other suffixes
    if (params && 'count' in params) {
      const count = Number(params.count);
      const pluralKey =
        count === 0 ? `${key}.zero` :
        count === 1 ? `${key}.one` :
        `${key}.other`;
      resolved = msgs[pluralKey] ?? msgs[key] ?? key;
    } else {
      resolved = msgs[key] ?? key;
    }

    // Variable interpolation: replace {name} with params.name
    if (params) {
      for (const [k, v] of Object.entries(params)) {
        resolved = resolved.replace(new RegExp(`\\{${k}\\}`, 'g'), String(v));
      }
    }

    return resolved;
  };
}
```

**No external i18n library needed.** This is ~30 lines of code. Keep it simple.

### Passing Locale to Components

The locale comes from `params.locale` in server components.

**Option: pass `t` function as prop (recommended for server components).**

```typescript
// app/[locale]/page.tsx
export default function HomePage({ params }: { params: { locale: Locale } }) {
  const t = createTranslator(params.locale);
  return <HomeContent t={t} locale={params.locale} />;
}
```

For client components that need translations, pass `t` as prop from the nearest server component parent. Do NOT use React Context for this — it would require making the layout a client component.

**Component signature pattern:**
```typescript
interface Props {
  t: TranslateFunction;
  locale: Locale;
  // ...existing props
}
```

## Root Redirect Page

`app/page.tsx` (outside `[locale]`) serves a client-side redirect:

```typescript
import { redirect } from 'next/navigation';
import { defaultLocale } from '@/lib/i18n/config';

export default function RootPage() {
  redirect(`/${defaultLocale}`);
}
```

For static export, also add a meta refresh fallback in a root `app/page.tsx` that renders:
```html
<meta http-equiv="refresh" content="0;url=/en/" />
```

## SEO Requirements

### `<html lang>` attribute

Set in `app/[locale]/layout.tsx`:
```tsx
<html lang={params.locale}>
```

### `hreflang` tags

Every page must include alternate links for both locales. Add in the locale layout's `<head>`:

```tsx
// app/[locale]/layout.tsx — in generateMetadata or <head>
<link rel="alternate" hreflang="en" href={`https://grapegeek.com/en${pathname}`} />
<link rel="alternate" hreflang="fr" href={`https://grapegeek.com/fr${pathname}`} />
<link rel="alternate" hreflang="x-default" href={`https://grapegeek.com/en${pathname}`} />
```

Since this is static export, compute `pathname` from params at build time (not from request).

### Translated metadata

`generateMetadata` in each page must use `t()` for titles and descriptions:

```typescript
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: `${t('varieties.title')} | GrapeGeek`,
    description: t('varieties.subtitle', { count: stats.total_varieties }),
  };
}
```

For dynamic pages (variety detail), the metadata uses a mix of `t()` for templates and DB values for proper nouns:
```typescript
// variety.name is never translated — it's a proper noun from the DB
const desc = `${variety.name} ${t('variety.grapeVariety')}`;
```

### Language Switcher

Add to `Header.tsx` — a simple toggle link that swaps `/en/` ↔ `/fr/` in the current URL path. The component receives `locale` as a prop and computes the alternate URL.

```tsx
// In Header: link to the other locale's version of the current page
const alternatePath = pathname.replace(`/${locale}/`, `/${otherLocale}/`);
```

**Note:** The Header becomes a client component (needs `usePathname()` for current URL). This is the only component that needs client-side routing awareness for the switcher.

## Translation Sync Script

### `scripts/sync_french.py`

Reuses the pattern from `utils/sync_french.py` (hash-based change detection, OpenAI translation). Adapted for JSON key-value format with per-entry hashing.

**Algorithm:**

1. Read `messages/en.json` (source of truth)
2. Read `messages/fr.json` (existing translations)
3. Read `messages/fr.hashes.json` (stored hashes per key)
4. For each key in `en.json`:
   - Compute `sha256(english_value)`
   - Compare with stored hash in `fr.hashes.json`
   - If hash matches → skip (already translated)
   - If hash differs or key is new → mark for translation
   - If key missing from `en.json` but present in `fr.json` → mark for deletion
5. Batch all keys needing translation into a single OpenAI API call
6. Update `fr.json` with new translations
7. Update `fr.hashes.json` with new hashes
8. Report: N new, N updated, N unchanged, N deleted

**OpenAI prompt template:**

```
Translate the following UI strings from English to French for a Quebec wine growing website.

Rules:
- Use Quebec French where appropriate
- Keep a friendly, approachable tone
- Preserve all {variable} placeholders exactly as-is — do not translate content inside {}
- Variable names like {variety}, {winegrower}, {count} are code placeholders
- Grape variety names inside {variety} are proper nouns and must NOT be translated
- Keep technical viticulture terms accurate
- For plural forms (.one/.other suffixes), maintain the same plural logic

Return a JSON object with the same keys and French translated values.

Strings to translate:
{json_subset}
```

**Per-entry hash storage (`messages/fr.hashes.json`):**

```json
{
  "nav.varieties": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "nav.winegrowers": "a1b2c3d4..."
}
```

**Dry-run support:** `--dry-run` flag shows what would be translated without calling OpenAI.

## Implementation Steps

Execute in this exact order. Each step should be a separate commit.

### Step 1: Create translation infrastructure

Files to create:
- `lib/i18n/config.ts` — locale constants
- `lib/i18n/translate.ts` — `createTranslator()` function with interpolation + plurals
- `lib/i18n/messages.ts` — message loading

No changes to existing components yet.

**Test:** Unit test `createTranslator` — verify interpolation, plural selection, missing key fallback.

### Step 2: Extract all English strings into `messages/en.json`

Read every component and page file. Extract every hardcoded user-facing string into `en.json` with namespaced keys. Use the key naming convention shown above.

Do NOT modify any component files yet. Just build the complete `en.json`.

**String count estimate:** ~200 keys.

Strings that are purely DB values (variety.name, city, country) are NOT extracted — they stay as-is.

### Step 3: Create initial `fr.json` via sync script

Files to create:
- `scripts/sync_french.py` — translation sync script
- `messages/fr.json` — generated by script
- `messages/fr.hashes.json` — generated by script

Run the script to produce the initial French translations.

**Test:** Verify all keys from `en.json` exist in `fr.json`. Verify all `{variables}` are preserved in French values. Verify `fr.hashes.json` has an entry for every key.

### Step 4: Restructure routes under `[locale]`

This is the largest step. Move all pages under `app/[locale]/`.

1. Create `app/[locale]/layout.tsx` with:
   - `generateStaticParams` returning both locales
   - `<html lang={locale}>`
   - `hreflang` meta tags
   - Pass locale to Header

2. Move every `app/*.tsx` and `app/*/` into `app/[locale]/`

3. Update every `generateStaticParams` in dynamic routes — they no longer need to return locale (parent handles it)

4. Create root `app/page.tsx` redirect to `/en/`

5. Keep `app/api/` outside `[locale]`

6. Update `next.config.js` if needed (add `trailingSlash: true` for clean static URLs)

**Test:** `npm run build` succeeds. Output directory contains `/en/` and `/fr/` subdirectories with identical page structures. All 600+ variety pages and 1400+ winegrower pages render for both locales.

At this point, both locales render but still show English text (strings not yet wired to `t()`).

### Step 5: Wire components to translation function

Migrate all components to use `t()` instead of hardcoded strings. Work through one component group at a time:

1. **Layout + Header** — nav items, footer, language switcher
2. **Homepage** — hero, stats, features
3. **Varieties** — index, filters, cards
4. **Variety detail** — info, section nav, winegrowers, production, research, photos
5. **Winegrowers** — index, filters, cards, header, info
6. **Map** — sidebar, popups, legend, loading states
7. **Stats** — stat boxes, chart cards, data quality
8. **Tree** — page content, loading
9. **About** — all prose content
10. **Error/not-found pages**

**Pattern for each component:**

```typescript
// Before
<h2>Grape Varieties</h2>
<p>{count} winegrowers growing {variety.name} in North America</p>

// After
<h2>{t('varieties.title')}</h2>
<p>{t('variety.winegrowers.count', { count, variety: variety.name })}</p>
```

**Critical rule:** Never put a variety/winegrower name inside a translation string as literal text. Always pass it as a `{variable}`. The French sentence structure may place the name in a different position:

```json
// en: "{count} winegrowers growing {variety} in North America"
// fr: "{count} vignobles cultivant {variety} en Amérique du Nord"
```

**Test:** After each component group, verify:
- English pages render identically to before
- French pages show French text with correct variable interpolation
- No hardcoded English strings remain in migrated components

### Step 6: Add language switcher to Header

Make Header a client component (needs `usePathname()`). Add a locale toggle that swaps `/en/` ↔ `/fr/` in the current path.

**Test:** Clicking the switcher navigates to the same page in the other language. The current page is highlighted correctly in nav.

### Step 7: Final SEO verification

- Verify `<html lang>` is correct per locale
- Verify `hreflang` tags are present on every page
- Verify `<title>` and `<meta description>` are translated
- Verify sitemap (if exists) includes both locale URLs
- Run `npm run build` and spot-check output HTML

## Component Migration Reference

### Props changes

Every component that renders user-facing text needs `t` and `locale` props added:

```typescript
// Before
interface Props {
  variety: GrapeVariety;
}

// After
interface Props {
  variety: GrapeVariety;
  t: TranslateFunction;
  locale: Locale;
}
```

Components that only render DB data (no UI labels) don't need changes.

### Link href changes

All internal links must include the locale prefix:

```typescript
// Before
<Link href="/varieties">

// After
<Link href={`/${locale}/varieties`}>
```

Create a helper if needed:
```typescript
function localePath(locale: Locale, path: string): string {
  return `/${locale}${path}`;
}
```

### Metadata changes

Every `generateMetadata` function receives `params.locale` and uses `t()`:

```typescript
export async function generateMetadata({ params }: { params: { locale: Locale; name: string } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  // ...
}
```

## What Does NOT Change

- Database schema and queries — all data stays English
- Route slugs — `/varieties/Marquette` same in both locales
- API routes — stay outside `[locale]`
- CSS/styling — no changes
- Variety names, winegrower names, wine names — proper nouns, never translated
- External links, VIVC references — unchanged
- Photo URLs and credits format — unchanged
