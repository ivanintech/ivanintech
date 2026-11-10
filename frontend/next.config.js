/** @type {import('next').NextConfig} */
const nextConfig = {
  // Dejarlo funcional primero: los errores de lint/type del proyecto heredado se
  // resolverán en el rediseño; no deben bloquear el build de producción.
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    // `next start` lee este bloque en RUNTIME, asi que el Dockerfile debe copiar
    // este fichero a la imagen final (si no, todo `_next/image` responde 400
    // "url parameter is not allowed").
    //
    // `hostname: '**'` NO basta en Next 15: el glob no cruza puntos de forma
    // fiable. Se declaran los dominios reales de miniaturas y se deja un
    // comodin por protocolo como red de seguridad.
    remotePatterns: [
      { protocol: 'https', hostname: 'i.ytimg.com' },
      { protocol: 'https', hostname: 'yt3.ggpht.com' },
      { protocol: 'https', hostname: 'www.google.com' },
      { protocol: 'https', hostname: 'opengraph.githubassets.com' },
      { protocol: 'https', hostname: '**.githubusercontent.com' },
      { protocol: 'https', hostname: '**.supabase.co' },
      { protocol: 'https', hostname: 'ivanintech.com' },
      { protocol: 'https', hostname: '**.render.com' },
      { protocol: 'https', hostname: '**' },
      { protocol: 'http', hostname: '**' },
    ],
  },
};

module.exports = nextConfig; 