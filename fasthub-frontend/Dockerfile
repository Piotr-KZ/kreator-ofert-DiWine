# Obraz bazowy - Node.js 20 na lekkim Alpine Linux
FROM node:20-alpine

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie package.json i package-lock.json (lista zależności)
COPY package*.json ./

# Instalacja zależności Node
RUN npm install

# Kopiowanie całego kodu frontendu
COPY . .

# Port na którym działa frontend
EXPOSE 3000

# Komenda uruchamiająca Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
