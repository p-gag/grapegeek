import Link from 'next/link';
import { AlertCircle } from 'lucide-react';

export default function VarietyNotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Variety Not Found</h1>
        <p className="text-gray-600 mb-6">
          The grape variety you&apos;re looking for doesn&apos;t exist in our database.
        </p>
        <div className="flex flex-col gap-3">
          <Link
            href="/varieties"
            className="px-6 py-3 bg-brand text-white rounded-lg hover:bg-brand-hover transition-colors font-medium"
          >
            Browse All Varieties
          </Link>
          <Link
            href="/"
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Go Home
          </Link>
        </div>
      </div>
    </div>
  );
}
