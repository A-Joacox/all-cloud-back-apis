FROM node:18-alpine

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install --only=production

# Copiar código fuente
COPY . .

# Agregar variables de entorno para el build
ENV MONGODB_URI=mongodb://mongodb:27017/cinema_movies
ENV NODE_ENV=production
ENV PORT=3001

# Construir la aplicación
RUN npm run build

# Exponer puerto
EXPOSE 3001

# Comando para iniciar la aplicación
CMD ["npm", "start"]