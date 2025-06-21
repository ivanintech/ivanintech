import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
  },
  eslint: {
    // Permite que la compilación de producción se complete incluso si hay errores de ESLint.
    // Esto es útil para desplegar rápidamente sin que te bloqueen errores de linting.
    ignoreDuringBuilds: true,
  },
  typescript: {
    // !! ADVERTENCIA !!
    // Permite peligrosamente que las compilaciones de producción se completen
    // incluso si tu proyecto tiene errores de tipo.
    ignoreBuildErrors: true,
  },
  async rewrites() {
    // En producción, todas las llamadas a /api/... serán redirigidas al backend
    if (process.env.NODE_ENV === 'production') {
      return [
        {
          source: '/api/:path*',
          destination: `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/:path*`,
        },
      ];
    }
    // En desarrollo, no hacemos nada, ya que el proxy ya está configurado de otra forma
    // o las llamadas son directas con CORS.
    return [];
  },
};

export default nextConfig;
