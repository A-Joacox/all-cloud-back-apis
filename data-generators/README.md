# Generadores de Datos para Microservicios de Cine

Scripts para generar 20,000 registros distribuidos entre las 3 bases de datos del sistema de cine.

## Distribución de Datos

### MongoDB (Movies API) - 8,000 registros
- **8,000 películas** con datos realistas
- **22 géneros** únicos
- Datos incluyen: títulos, descripciones, duración, géneros, directores, actores, fechas de estreno, ratings, etc.

### MySQL (Rooms API) - 12,000 registros
- **100 salas** con diferentes capacidades y tipos de pantalla
- **~15,000 asientos** distribuidos en las salas
- **12,000 horarios** de proyección con fechas y precios

### PostgreSQL (Reservations API) - 15,000 registros
- **2,000 usuarios** con datos personales
- **15,000 reservas** con diferentes estados
- **~45,000 asientos reservados** (1-6 asientos por reserva)
- **15,000 pagos** asociados a las reservas

## Instalación

### Node.js (MongoDB)
```bash
cd data-generators
npm install
```

### Python (MySQL y PostgreSQL)
```bash
pip install -r requirements.txt
```

## Configuración

1. Copiar archivo de configuración:
```bash
cp .env.example .env
```

2. Configurar variables de entorno en `.env`:
```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/cinema_movies

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
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