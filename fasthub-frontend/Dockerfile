# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Kopiowanie package.json i instalacja zależności
COPY package*.json ./
RUN npm ci

# Kopiowanie kodu
COPY . .

# Build argument for API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

# Budowanie z przekazaną zmienną
RUN npm run build

# Stage 2: Production
FROM nginx:alpine

# Kopiowanie zbudowanych plików do Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Kopiowanie konfiguracji Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Port 80 dla Nginx
EXPOSE 80

# Uruchomienie Nginx
CMD ["nginx", "-g", "daemon off;"]

