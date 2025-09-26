# Reservations API - Microservicio de Reservas

Microservicio para gestión de reservas, usuarios y pagos usando Spring Boot y PostgreSQL.

## Instalación

```bash
mvn clean install
```

## Variables de Entorno

Configurar las siguientes variables de entorno:

```env
DB_USERNAME=postgres
DB_PASSWORD=password
```

## Ejecución

```bash
mvn spring-boot:run
```

## Endpoints

### Usuarios
- `GET /api/users` - Listar usuarios
- `GET /api/users/:id` - Obtener usuario específico
- `POST /api/users` - Crear usuario
- `PUT /api/users/:id` - Actualizar usuario
- `DELETE /api/users/:id` - Eliminar usuario

### Reservas
- `GET /api/reservations` - Listar reservas
- `GET /api/reservations/:id` - Obtener reserva específica
- `GET /api/reservations/user/:userId` - Reservas de usuario
- `GET /api/reservations/movie/:movieId` - Reservas por película
- `POST /api/reservations` - Crear reserva
- `PUT /api/reservations/:id/cancel` - Cancelar reserva
- `DELETE /api/reservations/:id` - Eliminar reserva

### Pagos
- `POST /api/payments` - Procesar pago
- `GET /api/payments/reservation/:reservationId` - Obtener pago por reserva

## Estructura de Base de Datos

### Tabla: users
- id (SERIAL, PK)
- email (VARCHAR, UNIQUE)
- name (VARCHAR)
- phone (VARCHAR)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

### Tabla: reservations
- id (SERIAL, PK)
- user_id (INT, FK)
- schedule_id (INT) - Referencia a MySQL
- movie_id (VARCHAR) - Referencia a MongoDB
- total_amount (DECIMAL)
- status (ENUM)
- reservation_date (TIMESTAMP)

### Tabla: reserved_seats
- id (SERIAL, PK)
- reservation_id (INT, FK)
- seat_id (INT) - Referencia a MySQL

### Tabla: payments
- id (SERIAL, PK)
- reservation_id (INT, FK)
- amount (DECIMAL)
- payment_method (VARCHAR)
- payment_status (ENUM)
- transaction_id (VARCHAR)
- payment_date (TIMESTAMP)