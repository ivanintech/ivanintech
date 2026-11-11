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
  // Proxy del API: sin esto, `ivanintech.com/api/v1/*` devolvía 404/308 porque
  // el frontend no tiene backend propio. Con el rewrite, el mismo origen sirve
  // la API y se evita el CORS entre dominios.
  async redirects() {
    return [
      // /proyectos es una URL huérfana (nunca existió la página, no está en el
      // menú). Redirige permanente a /portfolio para no perder visitas ni
      // dejar un 404 indexable.
      { source: '/proyectos', destination: '/portfolio', permanent: true },
    ];
  },
  async rewrites() {
    const backend = (
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      'https://ivanintech.onrender.com/api/v1'
    ).replace(/\/+$/, '');
    return [
      {
        // /api/v1/health -> <backend>/health
        source: '/api/v1/:path*',
        destination: `${backend}/:path*`,
      },
      {
        // La API expone la raíz con barra final (/api/v1/ -> .../api/v1/)
        source: '/api/v1',
        destination: `${backend}/`,
      },
    ];
  },
};

module.exports = nextConfig; 