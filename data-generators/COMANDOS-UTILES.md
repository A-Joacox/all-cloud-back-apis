# 🛠️ COMANDOS ÚTILES PARA DESARROLLO

## 🐳 Docker Commands

### Iniciar solo las bases de datos
```bash
docker-compose up -d mongodb mysql postgresql
```

### Iniciar todo el sistema (APIs + Bases de datos)
```bash
docker-compose up -d
```

### Ver el estado de los contenedores
```bash
docker-compose ps
```

### Ver logs de un servicio específico
```bash
docker-compose logs mongodb
docker-compose logs mysql
docker-compose logs postgresql
```

### Reiniciar un servicio
```bash
docker-compose restart mysql
```

### Detener todo
```bash
docker-compose down
```

### Detener todo y eliminar volúmenes (CUIDADO: Borra datos)
```bash
docker-compose down -v
```

## 🗄️ Conexiones a Bases de Datos

### MongoDB
```bash
# Desde terminal
mongosh mongodb://localhost:27017/cinema_movies

# Comandos útiles
show collections
db.movies.countDocuments()
db.genres.find().pretty()
```

### MySQL  
```bash
# Desde terminal
mysql -h localhost -P 3307 -u cinema_user -p cinema_rooms

# Comandos útiles
SHOW TABLES;
SELECT COUNT(*) FROM rooms;
SELECT COUNT(*) FROM seats;
SELECT COUNT(*) FROM schedules;
```

### PostgreSQL
```bash
# Desde terminal
psql -h localhost -p 5432 -U cinema_user -d cinema_reservations

# Comandos útiles
\dt
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM reservations;
SELECT COUNT(*) FROM payments;
```

## 🔧 Desarrollo Local

### Reinstalar dependencias
```bash
cd data-generators
npm install
pip install -r requirements.txt
```

### Ejecutar generadores individuales
```bash
node mongodb-data-generator.js
python mysql-data-generator.py  
python postgresql-data-generator.py
```

### Verificar datos
```bash
node verify-data.js
```

## 🧹 Limpiar y Reiniciar

### Eliminar todos los datos y empezar limpio
```bash
docker-compose down -v
docker-compose up -d mongodb mysql postgresql
# Esperar 30 segundos
cd data-generators
run-all-generators.bat
```

### Solo limpiar datos (sin Docker)
```bash
# MongoDB
mongosh mongodb://localhost:27017/cinema_movies --eval "db.dropDatabase()"

# MySQL
mysql -h localhost -P 3307 -u cinema_user -p -e "DROP DATABASE IF EXISTS cinema_rooms; CREATE DATABASE cinema_rooms;"

# PostgreSQL  
psql -h localhost -p 5432 -U cinema_user -d postgres -c "DROP DATABASE IF EXISTS cinema_reservations; CREATE DATABASE cinema_reservations;"
```

## 📊 Verificar que Todo Funcione

### Probar APIs (después de levantar con docker-compose up -d)
```bash
# Movies API
curl http://localhost:3001/api/movies?limit=5

# Rooms API  
curl http://localhost:3002/api/rooms?limit=5

# Reservations API
curl http://localhost:3003/api/reservations?limit=5

# Gateway API (orquestador)
curl http://localhost:3004/api/showtimes?limit=5

# Analytics API
curl http://localhost:3005/api/analytics/dashboard
```

## 🚨 Solución de Problemas Comunes

### Error: Puerto en uso
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :3307

# Cambiar puerto en docker-compose.yml o detener el servicio
```

### Error: Conexión rechazada
```bash  
# Verificar que Docker esté corriendo
docker ps

# Reiniciar Docker Desktop si es necesario
```

### Error: Credenciales incorrectas
```bash
# Verificar .env
cat .env

# Usar credenciales de docker-compose.yml:
# MySQL: cinema_user / cinema_password
# PostgreSQL: cinema_user / cinema_password  
```

### Error: Dependencias faltantes
```bash
# Python
pip install mysql-connector-python psycopg2-binary python-dotenv

# Node.js
npm install mongodb mysql2 pg dotenv
```