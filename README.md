# Sistema de Microservicios para Cine

Sistema completo de microservicios para gestión de un cine, implementado con diferentes tecnologías y bases de datos según los requerimientos.

## Arquitectura

### Microservicios

1. **Movies API** (Next.js + MongoDB)
   - Puerto: 3001
   - Gestión de películas y géneros
   - Base de datos: MongoDB
   - **📚 Documentación API**: `http://localhost:3001/docs`

2. **Rooms API** (Python + MySQL)
   - Puerto: 3002
   - Gestión de salas, asientos y horarios
   - Base de datos: MySQL
   - **📚 Documentación API**: `http://localhost:3002/docs`

3. **Reservations API** (Java + PostgreSQL)
   - Puerto: 3003
   - Gestión de reservas, usuarios y pagos
   - Base de datos: PostgreSQL
   - **📚 Documentación API**: `http://localhost:3003/docs`

4. **Gateway API** (Node.js)
   - Puerto: 3004
   - Orquestador que consume otros microservicios
   - Endpoints unificados
   - **📚 Documentación API**: `http://localhost:3004/docs`

5. **Analytics API** (Node.js)
   - Puerto: 3005
   - Análisis de datos y métricas
   - Reportes y estadísticas
   - **📚 Documentación API**: `http://localhost:3005/docs`

## Bases de Datos

### MongoDB (Movies API)
- **Base de datos**: `cinema_movies`
- **Colecciones**: `movies`, `genres`
- **Documentos**: Estructura JSON para películas y géneros

### MySQL (Rooms API)
- **Base de datos**: `cinema_rooms`
- **Tablas**: `rooms`, `seats`, `schedules`
- **Relaciones**: 1:N entre rooms-seats y rooms-schedules

### PostgreSQL (Reservations API)
- **Base de datos**: `cinema_reservations`
- **Tablas**: `users`, `reservations`, `reserved_seats`, `payments`
- **Relaciones**: 1:N entre users-reservations, reservations-reserved_seats, 1:1 entre reservations-payments

## 📚 Documentación API con Swagger UI

Todos los microservicios incluyen documentación interactiva completa con **Swagger UI** accesible en el endpoint `/docs`:

### 🎯 URLs de Documentación

| Microservicio | URL de Documentación | Tecnología Swagger |
|---------------|---------------------|-------------------|
| **Movies API** | `http://localhost:3001/docs` | swagger-jsdoc + swagger-ui-react |
| **Rooms API** | `http://localhost:3002/docs` | Flasgger (Flask-Swagger) |
| **Reservations API** | `http://localhost:3003/docs` | SpringDoc OpenAPI 3 |
| **Gateway API** | `http://localhost:3004/docs` | swagger-jsdoc + swagger-ui-express |
| **Analytics API** | `http://localhost:3005/docs` | swagger-jsdoc + swagger-ui-express |

### ✨ Características de la Documentación

- **🔄 Interfaz Interactiva**: Prueba endpoints directamente desde el navegador
- **📋 Esquemas Completos**: Modelos de datos detallados para requests/responses
- **🏷️ Organización por Tags**: Endpoints agrupados lógicamente
- **📊 Ejemplos en Vivo**: Datos de ejemplo para cada endpoint
- **🚀 Try It Out**: Ejecuta requests reales con parámetros personalizables
- **📖 Descripciones Detalladas**: Documentación completa de cada operación

### 🛠️ Implementación Técnica

#### Next.js (Movies API)
```javascript
// swagger.config.js - Configuración OpenAPI 3.0
// app/docs/page.js - Componente React con SwaggerUI
```

#### Python Flask (Rooms API)
```python
# Flasgger con plantillas Swagger
# @swag_from decorators para endpoints
```

#### Java Spring Boot (Reservations API)
```java
// SpringDoc OpenAPI con anotaciones @Operation
// SwaggerConfig.java para configuración personalizada
```

#### Node.js Express (Gateway & Analytics)
```javascript
// swagger-jsdoc para generar especificación
// swagger-ui-express para interfaz web
```

### 🎮 Cómo Usar la Documentación

1. **Inicia el microservicio** que deseas explorar
2. **Navega a** `http://localhost:[PUERTO]/docs`
3. **Explora endpoints** organizados por categorías
4. **Prueba requests** usando "Try it out"
5. **Revisa responses** y códigos de estado

## Instalación y Ejecución

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar el repositorio
git clone <repository-url>
cd proyecto

# Ejecutar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Opción 2: Ejecución Manual

#### Prerrequisitos
- Node.js 18+
- Python 3.11+
- Java 17+
- MongoDB
- MySQL 8.0+
- PostgreSQL 15+

#### Movies API
```bash
cd movies-api
npm install
cp .env.example .env
# Configurar MONGODB_URI en .env
npm run dev
```

#### Rooms API
```bash
cd rooms-api
pip install -r requirements.txt
cp .env.example .env
# Configurar variables de MySQL en .env
python app.py
```

#### Reservations API
```bash
cd reservations-api
mvn clean install
# Configurar variables de PostgreSQL en application.yml
mvn spring-boot:run
```

#### Gateway API
```bash
cd gateway-api
npm install
cp .env.example .env
# Configurar URLs de otros servicios en .env
npm run dev
```

#### Analytics API
```bash
cd analytics-api
npm install
cp .env.example .env
# Configurar URLs de otros servicios en .env
npm run dev
```

## Endpoints Principales

### Movies API (http://localhost:3001)
- `GET /api/movies` - Listar películas
- `GET /api/movies/:id` - Obtener película
- `POST /api/movies` - Crear película
- `GET /api/movies/search?q=termino` - Buscar películas
- `GET /api/movies/featured` - Películas destacadas

### Rooms API (http://localhost:3002)
- `GET /api/rooms` - Listar salas
- `GET /api/rooms/:id/seats` - Asientos de sala
- `GET /api/schedules` - Listar horarios
- `POST /api/schedules` - Crear horario

### Reservations API (http://localhost:3003)
- `GET /api/users` - Listar usuarios
- `POST /api/users` - Crear usuario
- `GET /api/reservations` - Listar reservas
- `POST /api/reservations` - Crear reserva
- `POST /api/payments` - Procesar pago

### Gateway API (http://localhost:3004)
- `GET /api/showtimes` - Horarios completos
- `POST /api/book-ticket` - Reservar ticket
- `GET /api/user-dashboard/:userId` - Dashboard usuario
- `GET /api/movie-details/:movieId` - Detalles película

### Analytics API (http://localhost:3005)
- `GET /api/analytics/revenue` - Análisis ingresos
- `GET /api/analytics/popular-movies` - Películas populares
- `GET /api/analytics/occupancy` - Ocupación salas
- `GET /api/analytics/user-behavior` - Comportamiento usuarios
- `GET /api/analytics/dashboard` - Dashboard general

## Estructura del Proyecto

```
proyecto/
├── movies-api/                 # Next.js + MongoDB
├── rooms-api/                  # Python + MySQL
├── reservations-api/           # Java + PostgreSQL
├── gateway-api/                # Node.js Gateway
├── analytics-api/              # Node.js Analytics
├── database-designs/           # Esquemas de BD
├── docker-compose.yml          # Orquestación Docker
└── README.md                   # Este archivo
```

## Características Técnicas

### Cumplimiento de Requerimientos
- ✅ 3 microservicios con bases de datos propias
- ✅ 3 lenguajes de programación diferentes
- ✅ 3 bases de datos diferentes (2 SQL + 1 NoSQL)
- ✅ Al menos 2 tablas relacionadas en cada BD SQL
- ✅ Comunicación entre microservicios
- ✅ Documentación de estructuras de BD

### Tecnologías Utilizadas
- **Frontend/API**: Next.js, Python Flask, Java Spring Boot, Node.js
- **Bases de Datos**: MongoDB, MySQL, PostgreSQL
- **Contenedores**: Docker, Docker Compose
- **Comunicación**: HTTP REST APIs

### Patrones Implementados
- **Microservicios**: Separación de responsabilidades
- **API Gateway**: Punto de entrada unificado
- **Event Sourcing**: Comunicación asíncrona
- **CQRS**: Separación de comandos y consultas
- **Circuit Breaker**: Manejo de fallos

## Monitoreo y Logs

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f movies-api

# Ver estado de los servicios
docker-compose ps
```

## 🚀 Accesos Rápidos

Una vez que todos los servicios estén ejecutándose, puedes acceder a:

### 📋 Documentación Swagger UI
- **Movies API**: [http://localhost:3001/docs](http://localhost:3001/docs)
- **Rooms API**: [http://localhost:3002/docs](http://localhost:3002/docs)  
- **Reservations API**: [http://localhost:3003/docs](http://localhost:3003/docs)
- **Gateway API**: [http://localhost:3004/docs](http://localhost:3004/docs)
- **Analytics API**: [http://localhost:3005/docs](http://localhost:3005/docs)

### 🔍 Health Checks
- **Movies API**: [http://localhost:3001/health](http://localhost:3001/health)
- **Rooms API**: [http://localhost:3002/health](http://localhost:3002/health)
- **Reservations API**: [http://localhost:3003/health](http://localhost:3003/health) 
- **Gateway API**: [http://localhost:3004/health](http://localhost:3004/health)
- **Analytics API**: [http://localhost:3005/health](http://localhost:3005/health)

### 📊 Endpoints Principales
- **Películas**: `GET http://localhost:3001/api/movies`
- **Salas**: `GET http://localhost:3002/api/rooms`
- **Reservas**: `GET http://localhost:3003/api/reservations`
- **Horarios Orchestados**: `GET http://localhost:3004/api/showtimes`
- **Analytics Dashboard**: `GET http://localhost:3005/api/analytics/dashboard`

## Despliegue en AWS

Para desplegar en AWS, cada microservicio puede ser containerizado y desplegado en:
- **AWS ECS** para orquestación de contenedores
- **AWS RDS** para bases de datos gestionadas
- **AWS ELB** para balanceador de carga
- **AWS CloudWatch** para monitoreo

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.