import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "i.guim.co.uk" },
      { protocol: "https", hostname: "mediaproxy.salon.com" },
      { protocol: "https", hostname: "apicms.thestar.com.my" },
      { protocol: "https", hostname: "images.7news.com.au" },
      { protocol: "https", hostname: "www.americanbankingnews.com" },
      { protocol: "https", hostname: "www.livemint.com" },
      { protocol: "https", hostname: "img.etimg.com" },
      { protocol: "https", hostname: "www.thestreet.com" },
      // Añade aquí cualquier otro dominio de noticias que esperes
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
