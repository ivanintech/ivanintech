# Dockerfile for Next.js frontend

# 1. Base Image: Use the official Node.js image.
# Use a specific version for reproducibility.
FROM node:20-slim AS base

# 2. Set working directory
WORKDIR /app

# 3. Install dependencies
# Use a separate step for dependencies to leverage Docker's layer caching.
# First, copy over package.json and lock files.
COPY package.json yarn.lock* ./
# Install dependencies using yarn
RUN yarn install --frozen-lockfile

# 4. Build Stage: Build the Next.js application
FROM base AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Pass build arguments to the environment
ARG NEXT_PUBLIC_FIREBASE_API_KEY
ENV NEXT_PUBLIC_FIREBASE_API_KEY=$NEXT_PUBLIC_FIREBASE_API_KEY
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ENV NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID
ENV NEXT_PUBLIC_FIREBASE_PROJECT_ID=$NEXT_PUBLIC_FIREBASE_PROJECT_ID
ARG NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
ENV NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
ARG NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
ENV NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
ARG NEXT_PUBLIC_FIREBASE_APP_ID
ENV NEXT_PUBLIC_FIREBASE_APP_ID=$NEXT_PUBLIC_FIREBASE_APP_ID

# Build the Next.js application for production
RUN yarn build

# 5. Production Image: Create a smaller, more secure image for production.
# Use a clean base image
FROM node:20-slim AS production

# Set working directory
WORKDIR /app

# Copy the built application from the 'base' stage
COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/package.json ./yarn.lock* ./
COPY --from=base /app/node_modules ./node_modules

# Expose the port Next.js will run on
EXPOSE 3000

# Command to run the application
# Use the lightweight Next.js server
CMD ["yarn", "start"] 