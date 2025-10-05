'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to /docs automatically
    router.replace('/docs');
  }, [router]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      flexDirection: 'column',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      <h1>Movies API</h1>
      <p>Redirecting to API Documentation...</p>
      <a href="/docs" style={{ marginTop: '1rem', color: '#0070f3' }}>
        Go to API Docs
      </a>
    </div>
  );
}
