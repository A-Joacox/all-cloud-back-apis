# Gateway API - API Gateway

API Gateway que orquesta y consume otros microservicios del sistema de cine.

## Instalación

```bash
npm install
```

## Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
PORT=3004
MOVIES_API_URL=http://localhost:3001
ROOMS_API_URL=http://localhost:3002
RESERVATIONS_API_URL=http://localhost:3003
NODE_ENV=development
```

## Ejecución

```bash
npm run dev
```

## Endpoints Orquestados

### Endpoints Principales
- `GET /api/showtimes` - Horarios completos con información de películas y salas
- `POST /api/book-ticket` - Reservar ticket (orquesta múltiples servicios)
- `GET /api/user-dashboard/:userId` - Dashboard del usuario
- `GET /api/movie-details/:movieId` - Detalles completos de película

### Endpoints Proxy
- `GET|POST|PUT|DELETE /api/movies/*` - Proxy a Movies API
- `GET|POST|PUT|DELETE /api/rooms/*` - Proxy a Rooms API
- `GET|POST|PUT|DELETE /api/reservations/*` - Proxy a Reservations API
- `GET|POST|PUT|DELETE /api/users/*` - Proxy a Users API
- `GET|POST|PUT|DELETE /api/payments/*` - Proxy a Payments API

## Funcionalidades

1. **Orquestación de Servicios**: Combina datos de múltiples microservicios
2. **Proxy**: Redirige requests a los microservicios correspondientes
3. **Enriquecimiento de Datos**: Añade información relacionada de otros servicios
4. **Manejo de Errores**: Gestiona errores de servicios externos
5. **Health Check**: Monitoreo del estado del gateway

## Ejemplos de Uso

### Obtener horarios completos
```bash
GET /api/showtimes?movieId=123
```

### Reservar ticket
```bash
POST /api/book-ticket
{
  "userId": 1,
  "scheduleId": 5,
  "movieId": "123",
  "seatIds": [1, 2, 3],
  "totalAmount": 45.00
}
```

### Dashboard del usuario
```bash
GET /api/user-dashboard/1
```