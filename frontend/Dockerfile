# Dockerfile for Next.js frontend (IvanInTech)
# Corregido 25-oct-2026: el proyecto usa npm (Next 15, sin yarn.lock); el template usaba yarn -> npm.

# 1. Base Image: Use the official Node.js image.
FROM node:26-slim AS base

# NEXT_PUBLIC_* se embebe en el cliente durante `next build`; debe estar presente en esta etapa.
# IMPORTANTE: en Render hay que pasar esta variable como Build Arg o el bundle
# apuntara a localhost y TODAS las llamadas a la API fallaran en produccion.
ARG NEXT_PUBLIC_API_BASE_URL=https://ivanintech.onrender.com/api/v1
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL

# 2. Set working directory
WORKDIR /app

# 3. Install dependencies.
# Si existe package-lock.json se usa `npm ci` (reproducible y verifica el lock).
# Si no existe, se cae a `npm install`.
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci --no-audit --no-fund; \
    else \
      npm install --no-audit --no-fund; \
    fi

# 4. Build the application
COPY . .
RUN npm run build

# 5. Production Image
FROM node:26-slim AS production
WORKDIR /app
ENV NODE_ENV=production

COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/package.json ./package.json
COPY --from=base /app/node_modules ./node_modules
# next.config.js DEBE viajar a la imagen final: `next start` lo lee en runtime para
# resolver `images.remotePatterns`. Sin el, el optimizador rechaza cualquier URL
# externa con 400 "url parameter is not allowed" y todas las miniaturas se rompen.
COPY --from=base /app/next.config.js ./next.config.js

EXPOSE 3000
CMD ["npm", "run", "start"]
