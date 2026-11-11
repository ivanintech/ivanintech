// ivanintech/frontend/src/app/robots.ts
// Sirve /robots.txt y apunta al sitemap.
import type { MetadataRoute } from "next";

const BASE_URL = "https://ivanintech.com";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
        // Rutas privadas / de sesión: no aportan nada a un buscador.
        disallow: ["/login", "/register", "/api/", "/dashboard"],
      },
    ],
    sitemap: `${BASE_URL}/sitemap.xml`,
    host: BASE_URL,
  };
}
