# --- Build Stage ---
FROM node:20-alpine as builder

WORKDIR /app

# Install dependencies (including devDependencies for build)
COPY frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY frontend/ ./
RUN npm run build

# --- Production Stage ---
FROM nginx:stable-alpine as runner

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port
EXPOSE 80

# Use non-root nginx user (if available)
# The nginx image provides a nginx user; switch to it
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]