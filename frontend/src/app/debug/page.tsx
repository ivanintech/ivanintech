'use client';

import { useEffect, useState } from 'react';
import apiClient from '@/lib/api-client';

interface DebugInfo {
  clientSide: boolean;
  publicApiUrl: string | undefined;
  internalApiUrl: string | undefined;
  currentUrl: string;
}

interface ApiTestResult {
  success: boolean;
  count?: number;
  firstProject?: unknown;
  featuredCount?: number;
  error?: string;
}

export default function DebugPage() {
  const [debugInfo, setDebugInfo] = useState<DebugInfo>({} as DebugInfo);
  const [apiTest, setApiTest] = useState<ApiTestResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const debug = {
      clientSide: typeof window !== 'undefined',
      publicApiUrl: process.env.NEXT_PUBLIC_API_BASE_URL,
      internalApiUrl: process.env.INTERNAL_API_BASE_URL,
      currentUrl: window?.location?.href || 'N/A',
    };
    setDebugInfo(debug);

    // Test API call
    apiClient<unknown[]>('/projects/')
      .then((data) => {
        setApiTest({
          success: true,
          count: data.length,
          firstProject: data[0],
          featuredCount: data.filter(p => (p as { is_featured?: boolean }).is_featured).length,
        });
      })
      .catch((error) => {
        setApiTest({
          success: false,
          error: error.message,
        });
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Debug Information</h1>
      
      <div className="space-y-4">
        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">Environment</h2>
          <pre className="text-sm bg-gray-100 p-2 rounded">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>

        <div className="border p-4 rounded">
          <h2 className="text-lg font-semibold mb-2">API Test</h2>
          {loading ? (
            <p>Testing API connection...</p>
          ) : (
            <pre className="text-sm bg-gray-100 p-2 rounded">
              {JSON.stringify(apiTest, null, 2)}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
} 