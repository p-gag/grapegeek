import type { Metadata } from 'next'
import Link from 'next/link'
import { type Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: `${t('aiUsage.title')} | GrapeGeek`,
    description: t('aiUsage.description'),
  };
}

export default function AiUsagePage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">

        <h1 className="text-4xl font-bold text-gray-900 mb-3">{t('aiUsage.title')}</h1>
        <p className="text-gray-500 mb-8">{t('aiUsage.description')}</p>

        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 mb-4 rounded-r">
          <p className="font-semibold text-amber-800 mb-1">{t('aiUsage.disclosure.title')}</p>
          <p className="text-amber-900 text-sm leading-relaxed">{t('aiUsage.disclosure.text')}</p>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-10 rounded-r">
          <p className="font-semibold text-blue-800 mb-1">{t('aiUsage.quality.title')}</p>
          <p className="text-blue-900 text-sm leading-relaxed">{t('aiUsage.quality.text')}</p>
        </div>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('aiUsage.philosophy.title')}</h2>
          <p className="text-gray-700 leading-relaxed mb-4">{t('aiUsage.philosophy.p1')}</p>
          <p className="text-gray-700 leading-relaxed">{t('aiUsage.philosophy.p2')}</p>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">{t('aiUsage.process.title')}</h2>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">1. {t('aiUsage.process.repo.title')}</h3>
            <p className="text-gray-700 leading-relaxed mb-2">{t('aiUsage.process.repo.p1')}</p>
            <ul className="list-disc list-inside space-y-1 text-gray-700 mb-3">
              {t('aiUsage.process.repo.items').split('|').map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className="text-sm text-gray-500">{t('aiUsage.process.repo.tools')}</p>
            <p className="text-sm text-gray-500">{t('aiUsage.process.repo.role')}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">2. {t('aiUsage.process.content.title')}</h3>
            <p className="text-gray-700 leading-relaxed mb-2">{t('aiUsage.process.content.p1')}</p>
            <ul className="list-disc list-inside space-y-1 text-gray-700 mb-3">
              {t('aiUsage.process.content.items').split('|').map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className="text-sm text-gray-500">{t('aiUsage.process.content.tools')}</p>
            <p className="text-sm text-gray-500">{t('aiUsage.process.content.role')}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">3. {t('aiUsage.process.translation.title')}</h3>
            <p className="text-gray-700 leading-relaxed mb-3">{t('aiUsage.process.translation.p1')}</p>
            <p className="text-gray-700 leading-relaxed mb-2">{t('aiUsage.process.translation.p2')}</p>
            <ul className="list-disc list-inside space-y-1 text-gray-700 mb-3">
              {t('aiUsage.process.translation.items').split('|').map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
            <p className="text-sm text-gray-500">{t('aiUsage.process.translation.tools')}</p>
            <p className="text-sm text-gray-500">{t('aiUsage.process.translation.role')}</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">{t('aiUsage.forYou.title')}</h2>

          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">✅ {t('aiUsage.forYou.strengths.title')}</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              {t('aiUsage.forYou.strengths.items').split('|').map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">⚠️ {t('aiUsage.forYou.limitations.title')}</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-700">
              {t('aiUsage.forYou.limitations.items').split('|').map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">🎯 {t('aiUsage.forYou.bestPractice.title')}</h3>
            <p className="text-gray-700 leading-relaxed">{t('aiUsage.forYou.bestPractice.text')}</p>
          </div>
        </section>

        <section className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">{t('aiUsage.technical.title')}</h2>
          <p className="text-gray-700 leading-relaxed mb-3">{t('aiUsage.technical.p1')}</p>
          <ul className="list-disc list-inside space-y-2 text-gray-700 mb-4">
            <li>
              <strong>{t('aiUsage.technical.sourceCode')}</strong>{' '}
              <Link href="https://github.com/p-gag/grapegeek" className="text-brand hover:underline" target="_blank" rel="noopener noreferrer">
                github.com/p-gag/grapegeek
              </Link>
            </li>
            <li>{t('aiUsage.technical.models')}</li>
            <li>{t('aiUsage.technical.languages')}</li>
            <li>{t('aiUsage.technical.deployment')}</li>
          </ul>
          <p className="text-gray-700 leading-relaxed">{t('aiUsage.technical.p2')}</p>
        </section>

        <hr className="border-gray-200 my-8" />
        <p className="text-sm text-gray-500 italic">{t('aiUsage.footer')}</p>

      </div>
    </div>
  )
}
