# Rooms API - Microservicio de Salas

Microservicio para gestión de salas, asientos y horarios usando Python Flask y MySQL.

## Instalación

```bash
pip install -r requirements.txt
```

## Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=cinema_rooms
FLASK_ENV=development
FLASK_DEBUG=True
PORT=3002
```

## Ejecución

```bash
python app.py
```

## Endpoints

### Salas
- `GET /api/rooms` - Listar salas
- `GET /api/rooms/:id` - Obtener sala específica
- `POST /api/rooms` - Crear sala

### Asientos
- `GET /api/rooms/:id/seats` - Obtener asientos de una sala
- `POST /api/rooms/:id/seats` - Crear asientos para una sala

### Horarios
- `GET /api/schedules` - Listar horarios
- `POST /api/schedules` - Crear horario
- `GET /api/schedules/movie/:movieId` - Horarios por película

## Estructura de Base de Datos

### Tabla: rooms
- id (INT, PK)
- name (VARCHAR)
- capacity (INT)
- screen_type (ENUM: '2D', '3D', 'IMAX')
- is_active (BOOLEAN)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Tabla: seats
- id (INT, PK)
- room_id (INT, FK)
- row_number (VARCHAR)
- seat_number (INT)
- seat_type (ENUM: 'regular', 'premium', 'vip')
- is_available (BOOLEAN)
- created_at (TIMESTAMP)

### Tabla: schedules
- id (INT, PK)
- movie_id (VARCHAR) - Referencia a MongoDB
- room_id (INT, FK)
- show_time (DATETIME)
- price (DECIMAL)
- is_active (BOOLEAN)
- created_at (TIMESTAMP)