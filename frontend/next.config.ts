import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      // ¡ADVERTENCIA: Permite CUALQUIER hostname HTTPS! Usar con precaución.
      {
        protocol: 'https',
        hostname: '**', // <-- Comodín para cualquier hostname
      },
      // Eliminados los patrones específicos anteriores, ya que '**' los cubre.
      // Podrías añadir un patrón similar para 'http' si fuera necesario:
      // {
      //   protocol: 'http',
      //   hostname: '**',
      // },
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
