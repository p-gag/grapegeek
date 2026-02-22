import { Locale } from './config';
import { getMessages } from './messages';

export type TranslateFunction = (key: string, params?: Record<string, string | number>) => string;

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
