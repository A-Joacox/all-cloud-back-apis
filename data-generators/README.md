# 🎬 Generadores de Datos para Microservicios de Cine

Scripts automáticos para poblar las bases de datos con datos realistas para testing y desarrollo.

## 📊 ¿Qué se Genera?

| Base de Datos | Servicio | Registros | Descripción |
|---------------|----------|-----------|-------------|
| **MongoDB** | Movies API | ~8,000 | Películas realistas con géneros, directores, actores |
| **MySQL** | Rooms API | ~12,000 | Salas, asientos y horarios de proyección |
| **PostgreSQL** | Reservations API | ~15,000 | Usuarios, reservas y pagos del sistema |

**Total: ~35,000 registros** con relaciones correctas entre las bases de datos.

---

## 🚀 Inicio Rápido (Opción 1: Todo Automático)

### **Para Windows:**
```cmd
# 1. Iniciar las bases de datos con Docker
docker-compose up -d mongodb mysql postgresql

# 2. Ejecutar generador automático
run-all-generators.bat
```

### **Para Linux/Mac:**
```bash
# 1. Iniciar las bases de datos con Docker  
docker-compose up -d mongodb mysql postgresql

# 2. Ejecutar generador automático
./run-all-generators.sh
```

---

## 🛠️ Configuración Manual (Opción 2: Paso a Paso)

### **Paso 1: Levantar las Bases de Datos**

#### **Opción A: Con Docker (Recomendado)**
```bash
# Desde la raíz del proyecto
docker-compose up -d mongodb mysql postgresql

# Verificar que estén corriendo
docker-compose ps
```

#### **Opción B: Instalación Local**
- **MongoDB**: Puerto 27017
- **MySQL**: Puerto 3307, usuario: `cinema_user`, password: `cinema_password`
- **PostgreSQL**: Puerto 5432, usuario: `cinema_user`, password: `cinema_password`

### **Paso 2: Instalar Dependencias**

```bash
cd data-generators

# Dependencias de Node.js (para MongoDB)
npm install

# Dependencias de Python (para MySQL y PostgreSQL)
pip install -r requirements.txt
```

### **Paso 3: Configurar Variables de Entorno**

El archivo `.env` ya está configurado para Docker, pero puedes editarlo si necesitas:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/cinema_movies

# MySQL  
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_USER=cinema_user
MYSQL_PASSWORD=cinema_password
MYSQL_DATABASE=cinema_rooms

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=cinema_user
POSTGRES_PASSWORD=cinema_password
POSTGRES_DATABASE=cinema_reservations
```

---

## 🎯 Ejecutar Generadores

### **Opción 1: Todos a la vez (Recomendado)**
```bash
# Windows
run-all-generators.bat

# Linux/Mac
./run-all-generators.sh
```

### **Opción 2: Individual**
```bash
# MongoDB (Películas y géneros)
node mongodb-data-generator.js

# MySQL (Salas, asientos, horarios)
python mysql-data-generator.py

# PostgreSQL (Usuarios, reservas, pagos)  
python postgresql-data-generator.py
```

### **Verificar Datos Generados**
```bash
node verify-data.js
```

---

## 📋 Configuración de Docker Compose

Las credenciales están configuradas según tu `docker-compose.yml`:

```yaml
# MySQL
MYSQL_USER: cinema_user
MYSQL_PASSWORD: cinema_password  
MYSQL_DATABASE: cinema_rooms
Port: 3307 → 3306

# PostgreSQL
POSTGRES_USER: cinema_user
POSTGRES_PASSWORD: cinema_password
POSTGRES_DB: cinema_reservations  
Port: 5432 → 5432

# MongoDB
MONGO_INITDB_DATABASE: cinema_movies
Port: 27017 → 27017
```

---

## 🔍 Verificar Conexiones

### **Conectar a las Bases de Datos:**

```bash
# MongoDB
mongosh mongodb://localhost:27017/cinema_movies

# MySQL
mysql -h localhost -P 3307 -u cinema_user -p cinema_rooms

# PostgreSQL  
psql -h localhost -p 5432 -U cinema_user -d cinema_reservations
```

---

## ❗ Solución de Problemas

### **Error: Conexión Rechazada**
```
✅ Verificar que Docker esté corriendo: docker-compose ps
✅ Reiniciar contenedores: docker-compose restart
✅ Ver logs: docker-compose logs [servicio]
```

### **Error: Dependencias Faltantes**
```bash
# Para Python
pip install -r requirements.txt

# Para Node.js  
npm install
```

### **Error: Puerto en Uso**
```
✅ Cambiar puertos en docker-compose.yml
✅ O detener servicios: docker-compose down
```

### **Error: Datos Ya Existen**
```bash
# Limpiar bases de datos
docker-compose down -v  # Elimina volúmenes
docker-compose up -d    # Recrea contenedores
```

---

## 📁 Estructura de Archivos

```
data-generators/
├── mongodb-data-generator.js     # Genera películas y géneros
├── mysql-data-generator.py       # Genera salas, asientos, horarios  
├── postgresql-data-generator.py  # Genera usuarios, reservas, pagos
├── verify-data.js               # Verifica que los datos estén OK
├── run-all-generators.bat       # Script automático (Windows)
├── run-all-generators.sh        # Script automático (Linux/Mac)
├── package.json                 # Dependencias Node.js
├── requirements.txt             # Dependencias Python
├── .env                         # Configuración de conexiones
└── README.md                    # Este archivo
```

---

## 🎬 Datos Generados en Detalle

### **MongoDB - Movies API**
- ✅ **Géneros**: Action, Comedy, Drama, Horror, etc.
- ✅ **Películas**: Títulos, descripciones, directores, actores, ratings
- ✅ **Fechas**: Fechas de estreno realistas (1980-2024)
- ✅ **Relaciones**: Películas asignadas a géneros

### **MySQL - Rooms API**  
- ✅ **Salas**: Nombres únicos, capacidades, tipos de pantalla
- ✅ **Asientos**: Filas/columnas, tipos (regular/premium/vip)
- ✅ **Horarios**: Fechas futuras, precios variables por tipo de sala

### **PostgreSQL - Reservations API**
- ✅ **Usuarios**: Nombres, emails únicos, teléfonos
- ✅ **Reservas**: Estados realistas, referencias a movies/schedules
- ✅ **Pagos**: Métodos diversos, estados de pago
- ✅ **Asientos Reservados**: 1-6 asientos por reserva

---

## 🔗 Integración con APIs

Después de generar los datos, puedes:

1. **Iniciar todas las APIs**: `docker-compose up`
2. **Probar endpoints**: 
   - Movies API: http://localhost:3001/api/movies
   - Rooms API: http://localhost:3002/api/rooms
   - Reservations API: http://localhost:3003/api/reservations
3. **Gateway API**: http://localhost:3004 (orquesta todo)
4. **Analytics API**: http://localhost:3005/api/analytics

¡Listo para usar tu sistema de cine con datos realistas! 🎉
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=cinema_rooms

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=cinema_user
POSTGRES_PASSWORD=cinema_password
POSTGRES_DATABASE=cinema_reservations
```

## Ejecución

### Generar datos para MongoDB
```bash
npm run generate-mongodb
```

### Generar datos para MySQL
```bash
python mysql-data-generator.py
```

### Generar datos para PostgreSQL
```bash
python postgresql-data-generator.py
```

### Generar todos los datos
```bash
npm run generate-all
```

## Características de los Datos

### Datos Realistas
- **Nombres y apellidos** reales para usuarios
- **Títulos de películas** generados con palabras reales
- **Fechas** distribuidas en los últimos 2 años
- **Precios** realistas para tickets
- **Emails** únicos con formato válido
- **Teléfonos** con formato internacional

### Relaciones Consistentes
- **Foreign Keys** válidas entre tablas
- **Referencias cruzadas** entre microservicios
- **Estados** coherentes (reservas confirmadas tienen pagos completados)
- **Fechas** lógicas (reservas antes de pagos)

### Distribución Equilibrada
- **75% de registros activos** (is_active = true)
- **Variedad en tipos** de asientos, métodos de pago, géneros
- **Distribución temporal** realista
- **Capacidades** variadas para salas

## Verificación de Datos

### MongoDB
```javascript
// Verificar conteo de películas
db.movies.countDocuments()

// Verificar géneros únicos
db.genres.distinct("name").length

// Verificar películas activas
db.movies.countDocuments({isActive: true})
```

### MySQL
```sql
-- Verificar conteo de salas
SELECT COUNT(*) FROM rooms;

-- Verificar conteo de asientos
SELECT COUNT(*) FROM seats;

-- Verificar conteo de horarios
SELECT COUNT(*) FROM schedules;

-- Verificar asientos por sala
SELECT r.name, COUNT(s.id) as total_seats 
FROM rooms r 
LEFT JOIN seats s ON r.id = s.room_id 
GROUP BY r.id, r.name;
```

### PostgreSQL
```sql
-- Verificar conteo de usuarios
SELECT COUNT(*) FROM users;

-- Verificar conteo de reservas
SELECT COUNT(*) FROM reservations;

-- Verificar conteo de pagos
SELECT COUNT(*) FROM payments;

-- Verificar reservas por usuario
SELECT u.name, COUNT(r.id) as total_reservations
FROM users u
LEFT JOIN reservations r ON u.id = r.user_id
GROUP BY u.id, u.name
ORDER BY total_reservations DESC
LIMIT 10;
```

## Notas Importantes

1. **Ejecutar en orden**: Primero MongoDB, luego MySQL, finalmente PostgreSQL
2. **Verificar conexiones**: Asegurar que las bases de datos estén ejecutándose
3. **Espacio en disco**: Los datos generados requieren aproximadamente 500MB
4. **Tiempo de ejecución**: Proceso completo toma 5-10 minutos
5. **Datos únicos**: Los scripts manejan duplicados automáticamente

## Troubleshooting

### Error de conexión MongoDB
```bash
# Verificar que MongoDB esté ejecutándose
mongosh --eval "db.runCommand('ping')"
```

### Error de conexión MySQL
```bash
# Verificar conexión
mysql -h localhost -u root -p -e "SELECT 1"
```

### Error de conexión PostgreSQL
```bash
# Verificar conexión
psql -h localhost -U cinema_user -d cinema_reservations -c "SELECT 1"
```