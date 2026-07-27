# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . ./
RUN npm run build

# Production stage
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built app from build stage
COPY --from=build /app/dist .

# Create a default index.html redirect in case of SPA routing issues
RUN echo '<!DOCTYPE html><html><head><meta charset="utf-8"/><script>window.location.href="/";</script></head><body></body></html>' > /usr/share/nginx/html/index.html || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
