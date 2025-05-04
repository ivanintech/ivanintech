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
};

export default nextConfig;
