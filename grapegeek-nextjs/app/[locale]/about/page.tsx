import type { Metadata } from 'next'
import { type Locale } from '@/lib/i18n/config'
import { createTranslator } from '@/lib/i18n/translate'

export async function generateMetadata({ params }: { params: { locale: Locale } }): Promise<Metadata> {
  const t = createTranslator(params.locale);
  return {
    title: `${t('about.title')} | GrapeGeek`,
    description: t('about.mission.text'),
  };
}

export default function AboutPage({ params }: { params: { locale: Locale } }) {
  const { locale } = params;
  const t = createTranslator(locale);

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-6">{t('about.title')}</h1>

        <div className="prose prose-lg">
          <h2 className="text-2xl font-semibold mb-4">{t('about.mission.title')}</h2>
          <p className="mb-6 text-gray-700">
            {t('about.mission.text')}
          </p>

          <h2 className="text-2xl font-semibold mb-4">{t('about.whatWeDo.title')}</h2>
          <p className="mb-6 text-gray-700">
            {t('about.whatWeDo.text')}
          </p>

          <h2 className="text-2xl font-semibold mb-4">{t('about.technology.title')}</h2>
          <p className="mb-6 text-gray-700">
            {t('about.technology.text')}
          </p>

          <h2 className="text-2xl font-semibold mb-4">{t('about.dataSources.title')}</h2>
          <ul className="list-disc list-inside mb-6 text-gray-700 space-y-2">
            <li>{t('about.dataSources.item1')}</li>
            <li>{t('about.dataSources.item2')}</li>
            <li>{t('about.dataSources.item3')}</li>
            <li>{t('about.dataSources.item4')}</li>
          </ul>

          <h2 className="text-2xl font-semibold mb-4">{t('about.contact.title')}</h2>
          <p className="text-gray-700">
            {t('about.contact.text')}
          </p>
        </div>
      </div>
    </div>
  )
}
