# Dockerfile para Next.js frontend en producción (sin build interno)

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

# Copia solo los archivos necesarios para producción
COPY .next ./.next
COPY public ./public
COPY node_modules ./node_modules
COPY package.json ./package.json

EXPOSE 3000
CMD ["yarn", "start"] 