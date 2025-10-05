'use client';

import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';

// Importar SwaggerUI dinámicamente para evitar SSR issues
const SwaggerUI = dynamic(() => import('swagger-ui-react'), {
  ssr: false,
  loading: () => <div className="loading">Loading API Documentation...</div>
});

export default function DocsPage() {
  const [spec, setSpec] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSpec = async () => {
      try {
        const response = await fetch('/api/docs');
        if (!response.ok) {
          throw new Error('Failed to fetch API specification');
        }
        const data = await response.json();
        setSpec(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSpec();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading API Documentation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Error Loading Documentation</h1>
          <p className="text-gray-600">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <head>
        <title>Movies API Documentation</title>
        <meta name="description" content="Movies API OpenAPI Documentation" />
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.10.3/swagger-ui.css" />
      </head>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Movies API Documentation</h1>
                <p className="text-sm text-gray-600">Cinema Movies Microservice - MongoDB based API</p>
              </div>
              <div className="flex space-x-4">
                <a 
                  href="/api/movies" 
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  API Endpoint
                </a>
              </div>
            </div>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto">
          {spec && (
            <SwaggerUI
              spec={spec}
              docExpansion="list"
              deepLinking={true}
              displayRequestDuration={true}
              tryItOutEnabled={true}
              filter={true}
              layout="BaseLayout"
              supportedSubmitMethods={['get', 'post', 'put', 'delete', 'patch']}
            />
          )}
        </main>
      </div>

      <style jsx global>{`
        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 200px;
          font-size: 16px;
          color: #666;
        }
        
        .swagger-ui .topbar {
          display: none;
        }
        
        .swagger-ui .info {
          margin: 20px 0;
        }
        
        .swagger-ui .scheme-container {
          background: #fafafa;
          padding: 15px;
          border-radius: 4px;
          margin: 20px 0;
        }
      `}</style>
    </>
  );
}