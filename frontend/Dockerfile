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

# 4. Build the application
# Copy the rest of the source code
COPY . .
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