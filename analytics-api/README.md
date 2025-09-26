# Analytics API - Microservicio Analítico

Microservicio para análisis de datos, reportes y métricas del sistema de cine.

## Instalación

```bash
npm install
```

## Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
PORT=3005
MOVIES_API_URL=http://localhost:3001
ROOMS_API_URL=http://localhost:3002
RESERVATIONS_API_URL=http://localhost:3003
NODE_ENV=development
```

## Ejecución

```bash
npm run dev
```

## Endpoints

### Análisis de Ingresos
- `GET /api/analytics/revenue` - Análisis de ingresos por período
- Parámetros: `period` (day|week|month|year), `startDate`, `endDate`

### Películas Populares
- `GET /api/analytics/popular-movies` - Películas más populares
- Parámetros: `limit`, `period`

### Ocupación de Salas
- `GET /api/analytics/occupancy` - Análisis de ocupación de salas
- Parámetros: `period`, `roomId`

### Comportamiento de Usuarios
- `GET /api/analytics/user-behavior` - Análisis de comportamiento de usuarios
- Parámetros: `period`

### Dashboard General
- `GET /api/analytics/dashboard` - Métricas generales del sistema
- Parámetros: `period`

## Funcionalidades

1. **Análisis de Ingresos**: Cálculo de ingresos por período, tendencias
2. **Películas Populares**: Ranking de películas por reservas
3. **Ocupación de Salas**: Análisis de utilización de salas
4. **Comportamiento de Usuarios**: Segmentación y análisis de usuarios
5. **Dashboard**: Métricas generales del sistema

## Ejemplos de Uso

### Análisis de ingresos del último mes
```bash
GET /api/analytics/revenue?period=month
```

### Top 10 películas más populares
```bash
GET /api/analytics/popular-movies?limit=10&period=month
```

### Ocupación de salas por semana
```bash
GET /api/analytics/occupancy?period=week
```

### Dashboard general
```bash
GET /api/analytics/dashboard?period=month
```