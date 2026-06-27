# --- Build Stage ---
FROM node:20-alpine as builder

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Production Stage ---
FROM nginx:stable-alpine as runner

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx configuration can be copied here if needed
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
