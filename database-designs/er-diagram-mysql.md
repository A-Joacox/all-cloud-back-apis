# Diagrama ER - MySQL (Salas y Asientos)

## Entidades

### 1. ROOMS (Salas)
- **id** (INT, PK): Identificador único de la sala
- **name** (VARCHAR): Nombre de la sala
- **capacity** (INT): Capacidad de la sala
- **screen_type** (ENUM): Tipo de pantalla (2D, 3D, IMAX)
- **is_active** (BOOLEAN): Estado activo/inactivo
- **created_at** (TIMESTAMP): Fecha de creación
- **updated_at** (TIMESTAMP): Fecha de última actualización

### 2. SEATS (Asientos)
- **id** (INT, PK): Identificador único del asiento
- **room_id** (INT, FK): Referencia a la sala
- **row_number** (VARCHAR): Número de fila (A, B, C, etc.)
- **seat_number** (INT): Número del asiento en la fila
- **seat_type** (ENUM): Tipo de asiento (regular, premium, vip)
- **is_available** (BOOLEAN): Disponibilidad del asiento
- **created_at** (TIMESTAMP): Fecha de creación

### 3. SCHEDULES (Horarios)
- **id** (INT, PK): Identificador único del horario
- **movie_id** (VARCHAR): Referencia a película en MongoDB
- **room_id** (INT, FK): Referencia a la sala
- **show_time** (DATETIME): Fecha y hora de la función
- **price** (DECIMAL): Precio del ticket
- **is_active** (BOOLEAN): Estado activo/inactivo
- **created_at** (TIMESTAMP): Fecha de creación

## Relaciones

```
ROOMS (1) -----> (N) SEATS
ROOMS (1) -----> (N) SCHEDULES
```

### Relación ROOMS-SEATS
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Una sala puede tener muchos asientos
- **Restricción**: CASCADE DELETE (al eliminar una sala, se eliminan sus asientos)

### Relación ROOMS-SCHEDULES
- **Tipo**: Uno a Muchos (1:N)
- **Descripción**: Una sala puede tener muchos horarios
- **Restricción**: CASCADE DELETE (al eliminar una sala, se eliminan sus horarios)

## Restricciones

1. **Unique Constraint**: `(room_id, row_number, seat_number)` - Cada asiento debe ser único dentro de una sala
2. **Foreign Key**: `seats.room_id` → `rooms.id`
3. **Foreign Key**: `schedules.room_id` → `rooms.id`
4. **Check Constraints**: 
   - `capacity > 0`
   - `price > 0`
   - `seat_number > 0`

## Índices

1. **idx_rooms_active**: `rooms(is_active)` - Para filtrar salas activas
2. **idx_seats_room**: `seats(room_id)` - Para buscar asientos por sala
3. **idx_seats_available**: `seats(is_available)` - Para filtrar asientos disponibles
4. **idx_schedules_movie**: `schedules(movie_id)` - Para buscar horarios por película
5. **idx_schedules_room**: `schedules(room_id)` - Para buscar horarios por sala
6. **idx_schedules_time**: `schedules(show_time)` - Para ordenar por fecha/hora
7. **idx_schedules_active**: `schedules(is_active)` - Para filtrar horarios activos