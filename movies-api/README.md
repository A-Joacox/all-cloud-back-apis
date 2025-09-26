# Movies API - Microservicio de Películas

Microservicio para gestión de películas usando Next.js y MongoDB.

## Instalación

```bash
npm install
```

## Variables de Entorno

Crear archivo `.env` basado en `.env.example`:

```env
MONGODB_URI=mongodb://localhost:27017/cinema_movies
PORT=3001
NODE_ENV=development
```

## Ejecución

```bash
# Desarrollo
npm run dev

# Producción
npm run build
npm start
```

## Endpoints

### Películas
- `GET /api/movies` - Listar películas
- `GET /api/movies/:id` - Obtener película específica
- `POST /api/movies` - Crear película
- `PUT /api/movies/:id` - Actualizar película
- `DELETE /api/movies/:id` - Eliminar película
- `GET /api/movies/search?q=termino&genre=action` - Buscar películas
- `GET /api/movies/featured` - Películas destacadas

### Géneros
- `GET /api/genres` - Listar géneros
- `POST /api/genres` - Crear género

## Estructura de Datos

### Película
```json
{
  "title": "string",
  "description": "string",
  "duration": "number",
  "genre": ["string"],
  "director": "string",
  "cast": ["string"],
  "releaseDate": "Date",
  "rating": "number",
  "posterUrl": "string",
  "trailerUrl": "string",
  "isActive": "boolean"
}
```