import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'About | GrapeGeek',
  description: 'Learn about the GrapeGeek project and cold-climate viticulture research',
}

export default function AboutPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-bold mb-6">About GrapeGeek</h1>

        <div className="prose prose-lg">
          <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
          <p className="mb-6 text-gray-700">
            GrapeGeek is a comprehensive research project mapping winegrowers
            and grape varieties across northeastern North America, with a particular
            focus on cold-climate viticulture and hybrid grape varieties.
          </p>

          <h2 className="text-2xl font-semibold mb-4">What We Do</h2>
          <p className="mb-6 text-gray-700">
            We collect, verify, and organize data about winegrowers, their wines,
            and the grape varieties they grow. Our database includes information from
            official regulatory sources combined with detailed research about grape
            genetics and viticulture characteristics.
          </p>

          <h2 className="text-2xl font-semibold mb-4">The Technology</h2>
          <p className="mb-6 text-gray-700">
            This site is built with Next.js using Static Site Generation (SSG) for
            optimal performance and SEO. Data is stored in a SQLite database built
            from authoritative JSONL source files, enabling complex queries and
            relationships while maintaining data integrity.
          </p>

          <h2 className="text-2xl font-semibold mb-4">Data Sources</h2>
          <ul className="list-disc list-inside mb-6 text-gray-700 space-y-2">
            <li>Official government wine producer registries</li>
            <li>VIVC (Vitis International Variety Catalogue)</li>
            <li>Winegrower websites and published materials</li>
            <li>Industry associations and trade groups</li>
          </ul>

          <h2 className="text-2xl font-semibold mb-4">Contact</h2>
          <p className="text-gray-700">
            Questions or suggestions? Feel free to reach out through our GitHub repository
            or contact the project maintainers.
          </p>
        </div>
      </div>
    </div>
  )
}
