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
};

export default nextConfig;
