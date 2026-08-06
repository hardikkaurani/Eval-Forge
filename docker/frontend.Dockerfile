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

# Remove default nginx static assets and config
RUN rm -rf /usr/share/nginx/html/* /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Grant permissions for non-root nginx worker
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

# Expose port
EXPOSE 80

# Use non-root nginx user
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]