/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // Permite imágenes de cualquier dominio usando un loader personalizado
    loader: 'imgix',
    path: '', // Esto permite cualquier dominio, pero debes usar src absoluto
    // Si quieres usar el loader default y permitir todos los dominios, Next.js no lo permite por seguridad.
    // Alternativamente, puedes usar <img> estándar en vez de <Image> para no tener restricciones.
  },
};

module.exports = nextConfig; 