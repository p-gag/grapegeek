import type { Locale } from '@/lib/i18n/config';
import { createTranslator } from '@/lib/i18n/translate';

interface DataDisclaimerProps {
  type?: 'variety' | 'producer';
  locale: Locale;
}

export default function DataDisclaimer({ type = 'variety', locale }: DataDisclaimerProps) {
  const t = createTranslator(locale);
  const text = type === 'variety'
    ? t('variety.disclaimer.variety')
    : t('variety.disclaimer.producer');

  return (
    <div className="data-disclaimer-footer">
      <div className="disclaimer-content">
        <div className="disclaimer-text">
          <span>ℹ️</span>
          <span>{text}</span>
        </div>
      </div>
    </div>
  );
}
