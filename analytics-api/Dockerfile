FROM node:18-alpine

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package*.json ./

# Instalar dependencias
RUN npm install --only=production

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 3005

# Comando para iniciar la aplicación
CMD ["npm", "start"]