import type { Metadata } from 'next'
import Link from 'next/link'
import { type Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: `${t('about.title')} | GrapeGeek`,
    description: t('about.project.p1'),
  };
}

export default function AboutPage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">

        <h1 className="text-4xl font-bold text-gray-900 mb-8">{t('about.title')}</h1>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('about.project.title')}</h2>
          <p className="text-gray-700 leading-relaxed">{t('about.project.p1')}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('about.ai.title')}</h2>
          <p className="text-gray-700 leading-relaxed mb-3">{t('about.ai.p1')}</p>
          <p className="text-gray-700 leading-relaxed">
            {t('about.ai.p2')}{' '}
            <Link href={`/${locale}/ai-usage`} className="text-brand hover:underline font-medium">
              {t('about.ai.p2Link')}
            </Link>{' '}
            {t('about.ai.p2After')}
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('about.biases.title')}</h2>
          <p className="text-gray-700 leading-relaxed mb-4">{t('about.biases.intro')}</p>
          <p className="text-gray-700 leading-relaxed mb-4">
            <strong className="text-gray-900">{t('about.biases.cold.label')}</strong>{' '}
            {t('about.biases.cold.text')}
          </p>
          <p className="text-gray-700 leading-relaxed">
            <strong className="text-gray-900">{t('about.biases.quebec.label')}</strong>{' '}
            {t('about.biases.quebec.text')}
          </p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('about.author.title')}</h2>
          <p className="text-gray-700 leading-relaxed mb-4">{t('about.author.p1')}</p>
          <p className="text-gray-700 leading-relaxed mb-4">{t('about.author.p2')}</p>
          <p className="text-gray-700 leading-relaxed mb-4">{t('about.author.p3')}</p>
          <p className="text-gray-700 leading-relaxed">{t('about.author.p4')}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('about.summary.title')}</h2>
          <ul className="space-y-4">
            <li className="text-gray-700 leading-relaxed">
              <strong className="text-gray-900">{t('about.summary.hybrids.label')}</strong>{' '}
              {t('about.summary.hybrids.text')}
            </li>
            <li className="text-gray-700 leading-relaxed">
              <strong className="text-gray-900">{t('about.summary.casual.label')}</strong>{' '}
              {t('about.summary.casual.text')}
            </li>
            <li className="text-gray-700 leading-relaxed">
              <strong className="text-gray-900">{t('about.summary.facts.label')}</strong>{' '}
              {t('about.summary.facts.text')}
            </li>
          </ul>
        </section>

      </div>
    </div>
  )
}
