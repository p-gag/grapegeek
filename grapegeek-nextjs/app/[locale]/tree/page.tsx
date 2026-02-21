'use client';

import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';

// Dynamically import the tree content to avoid SSR issues with ReactFlow
const TreePageContent = dynamic(() => import('@/components/tree/TreePageContent'), {
  ssr: false,
  loading: () => (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100vh',
      color: '#666',
      fontSize: '18px'
    }}>
      Loading family tree...
    </div>
  )
});

interface PageProps {
  params: { locale: string };
}

function TreePageInner({ locale }: { locale: string }) {
  const searchParams = useSearchParams();
  const variety = searchParams.get('variety');

  if (!variety) {
    return (
      <div style={{ padding: '4rem 2rem', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
          🌳 Family Tree Browser
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#666', marginBottom: '2rem' }}>
          No variety specified
        </p>
        <Link
          href={`/${locale}/varieties`}
          style={{
            display: 'inline-block',
            padding: '0.75rem 1.5rem',
            background: '#8B5CF6',
            color: 'white',
            borderRadius: '8px',
            textDecoration: 'none'
          }}
        >
          ← Browse Varieties
        </Link>
      </div>
    );
  }

  return <TreePageContent initialVariety={variety} locale={locale} />;
}

export default function TreePage({ params }: PageProps) {
  const { locale } = params;
  return (
    <Suspense fallback={<div style={{ padding: '4rem 2rem', textAlign: 'center' }}>Loading...</div>}>
      <TreePageInner locale={locale} />
    </Suspense>
  );
}
