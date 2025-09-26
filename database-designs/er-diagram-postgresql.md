# Diagrama ER - PostgreSQL (Reservas y Pagos)

## Entidades

### 1. USERS (Usuarios)
- **id** (SERIAL, PK): Identificador único del usuario
- **email** (VARCHAR, UNIQUE): Email del usuario (único)
- **name** (VARCHAR): Nombre del usuario
- **phone** (VARCHAR): Teléfono del usuario
- **created_at** (TIMESTAMP): Fecha de creación
- **updated_at** (TIMESTAMP): Fecha de última actualización

### 2. RESERVATIONS (Reservas)
- **id** (SERIAL, PK): Identificador único de la reserva
- **user_id** (INTEGER, FK): Referencia al usuario
- **schedule_id** (INTEGER): Referencia a horario en MySQL
- **movie_id** (VARCHAR): Referencia a película en MongoDB
- **total_amount** (DECIMAL): Monto total de la reserva
- **status** (VARCHAR): Estado de la reserva (PENDING, CONFIRMED, CANCELLED, EXPIRED)
- **reservation_date** (TIMESTAMP): Fecha de la reserva

### 3. RESERVED_SEATS (Asientos Reservados)
- **id** (SERIAL, PK): Identificador único del asiento reservado
- **reservation_id** (INTEGER, FK): Referencia a la reserva
- **seat_id** (INTEGER): Referencia a asiento en MySQL

### 4. PAYMENTS (Pagos)
- **id** (SERIAL, PK): Identificador único del pago
- **reservation_id** (INTEGER, FK): Referencia a la reserva
- **amount** (DECIMAL): Monto del pago
- **payment_method** (VARCHAR): Método de pago
- **payment_status** (VARCHAR): Estado del pago (PENDING, COMPLETED, FAILED, REFUNDED)
- **transaction_id** (VARCHAR): ID de la transacción
- **payment_date** (TIMESTAMP): Fecha del pago

## Relaciones

```
USERS (1) -----> (N) RESERVATIONS
RESERVATIONS (1) -----> (N) RESERVED_SEATS
RESERVATIONS (1) -----> (1) PAYMENTS
```

### Relación USERS-RESERVATIONS
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Un usuario puede tener muchas reservas
- **Restricción**: CASCADE DELETE (al eliminar un usuario, se eliminan sus reservas)

### Relación RESERVATIONS-RESERVED_SEATS
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Una reserva puede tener muchos asientos reservados
- **Restricción**: CASCADE DELETE (al eliminar una reserva, se eliminan sus asientos reservados)

### Relación RESERVATIONS-PAYMENTS
- **Tipo**: Uno a Uno (1:1)
- **Descripción**: Una reserva puede tener un pago
- **Restricción**: CASCADE DELETE (al eliminar una reserva, se elimina su pago)

## Restricciones

1. **Unique Constraint**: `users(email)` - Email único por usuario
2. **Foreign Key**: `reservations.user_id` → `users.id`
3. **Foreign Key**: `reserved_seats.reservation_id` → `reservations.id`
4. **Foreign Key**: `payments.reservation_id` → `reservations.id`
5. **Check Constraints**: 
   - `total_amount > 0`
   - `amount > 0`
   - `status IN ('PENDING', 'CONFIRMED', 'CANCELLED', 'EXPIRED')`
   - `payment_status IN ('PENDING', 'COMPLETED', 'FAILED', 'REFUNDED')`

## Índices

1. **idx_users_email**: `users(email)` - Para búsquedas por email
2. **idx_reservations_user**: `reservations(user_id)` - Para buscar reservas por usuario
3. **idx_reservations_movie**: `reservations(movie_id)` - Para buscar reservas por película
4. **idx_reservations_schedule**: `reservations(schedule_id)` - Para buscar reservas por horario
5. **idx_reservations_status**: `reservations(status)` - Para filtrar por estado
6. **idx_reservations_date**: `reservations(reservation_date)` - Para ordenar por fecha
7. **idx_reserved_seats_reservation**: `reserved_seats(reservation_id)` - Para buscar asientos por reserva
8. **idx_payments_reservation**: `payments(reservation_id)` - Para buscar pagos por reserva
9. **idx_payments_status**: `payments(payment_status)` - Para filtrar por estado de pago

## Triggers

### Trigger para actualizar updated_at
- **Función**: `update_updated_at_column()`
- **Tabla**: `users`
- **Evento**: BEFORE UPDATE
- **Descripción**: Actualiza automáticamente el campo `updated_at` cuando se modifica un usuario