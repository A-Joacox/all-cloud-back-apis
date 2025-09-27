# Servicio de Ingesta de Datos AWS

Servicio de migración y sincronización de datos del sistema de cine a servicios de AWS usando boto3.

## Características

- **Migración completa**: Migra todos los datos de MySQL, PostgreSQL y MongoDB a AWS
- **Backup automático**: Respaldo periódico de datos a Amazon S3
- **Sincronización en tiempo real**: Sincronización incremental con DynamoDB
- **API REST**: Endpoints para control manual de migraciones
- **Monitoreo**: Logs detallados y reportes de migración
- **Escalabilidad**: Procesamiento en lotes y manejo de errores

## Arquitectura

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Local DBs     │    │  Data Ingestion  │    │   AWS Services  │
│                 │    │     Service      │    │                 │
│ ┌─────────────┐ │    │                  │    │ ┌─────────────┐ │
│ │   MySQL     │ │───▶│  ┌─────────────┐ │───▶│ │     S3      │ │
│ │  (Rooms)    │ │    │  │  Migration  │ │    │ │  (Backups)  │ │
│ └─────────────┘ │    │  │   Service   │ │    │ └─────────────┘ │
│                 │    │  └─────────────┘ │    │                 │
│ ┌─────────────┐ │    │                  │    │ ┌─────────────┐ │
│ │PostgreSQL   │ │───▶│  ┌─────────────┐ │───▶│ │  DynamoDB   │ │
│ │(Reservations)│ │    │  │   S3        │ │    │ │  (NoSQL)    │ │
│ └─────────────┘ │    │  │  Service    │ │    │ └─────────────┘ │
│                 │    │  └─────────────┘ │    │                 │
│ ┌─────────────┐ │    │                  │    │ ┌─────────────┐ │
│ │  MongoDB    │ │───▶│  ┌─────────────┐ │───▶│ │    RDS      │ │
│ │  (Movies)   │ │    │  │ DynamoDB    │ │    │ │ (Analytics) │ │
│ └─────────────┘ │    │  │  Service    │ │    │ └─────────────┘ │
└─────────────────┘    │  └─────────────┘ │    └─────────────────┘
                       │                  │
                       │  ┌─────────────┐ │
                       │  │   Flask     │ │
                       │  │    API      │ │
                       │  └─────────────┘ │
                       └──────────────────┘
```

## Servicios AWS Utilizados

### Amazon S3
- **Propósito**: Backup y almacenamiento de datos históricos
- **Estructura**:
  ```
  cinema-data-bucket/
  ├── backups/
  │   ├── mysql/
  │   │   ├── rooms/
  │   │   ├── seats/
  │   │   └── schedules/
  │   ├── postgresql/
  │   │   ├── users/
  │   │   ├── reservations/
  │   │   ├── reserved_seats/
  │   │   └── payments/
  │   └── mongodb/
  │       ├── movies/
  │       └── genres/
  └── analytics/
      ├── migration_reports/
      └── analytics_data/
  ```

### Amazon DynamoDB
- **Propósito**: Base de datos NoSQL para consultas rápidas
- **Tablas**:
  - `cinema-movies`: Películas con índices por género
  - `cinema-rooms`: Salas con índices por tipo de pantalla
  - `cinema-reservations`: Reservas con índices por usuario y película
  - `cinema-users`: Usuarios con índice por email

### Amazon RDS (Opcional)
- **Propósito**: Data warehouse para analytics avanzados
- **Configuración**: PostgreSQL para consultas complejas

## Instalación

### Prerrequisitos

1. **Python 3.11+**
2. **Credenciales AWS** configuradas
3. **Docker** (opcional)
4. **Redis** (para tareas programadas)

### Instalación Local

```bash
# Clonar el repositorio
cd data-ingestion-service

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp env.example .env
# Editar .env con tus credenciales AWS

# Configurar recursos AWS
python scripts/setup_aws_resources.py
```

### Instalación con Docker

```bash
# Desde el directorio raíz del proyecto
cp env.docker.example .env.docker
# Editar .env.docker con tus credenciales

# Ejecutar con docker-compose
docker-compose up -d data-ingestion-service
```

## Configuración

### Variables de Entorno

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=cinema-data-bucket
S3_BACKUP_FOLDER=backups
S3_ANALYTICS_FOLDER=analytics

# DynamoDB Configuration
DYNAMODB_MOVIES_TABLE=cinema-movies
DYNAMODB_ROOMS_TABLE=cinema-rooms
DYNAMODB_RESERVATIONS_TABLE=cinema-reservations
DYNAMODB_USERS_TABLE=cinema-users

# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=cinema_rooms

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DATABASE=cinema_reservations

MONGODB_URI=mongodb://localhost:27017/cinema_movies
```

### Configuración de AWS

1. **Crear bucket S3**:
   ```bash
   aws s3 mb s3://cinema-data-bucket
   ```

2. **Configurar DynamoDB**:
   ```bash
   python scripts/setup_aws_resources.py
   ```

3. **Configurar IAM**:
   - Crear usuario con permisos para S3, DynamoDB y RDS
   - O usar roles IAM para EC2/ECS

## Uso

### Modos de Ejecución

#### 1. API REST (Recomendado)
```bash
python main.py --mode api --port 3006
```

#### 2. Migración Única
```bash
python main.py --mode migrate
```

#### 3. Backup Único
```bash
python main.py --mode backup
```

#### 4. Scheduler
```bash
python main.py --mode scheduler
```

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Migración Completa
```bash
POST /migrate
```

#### Backup Manual
```bash
POST /backup
```

#### Sincronización Incremental
```bash
POST /sync/{table_name}
Content-Type: application/json
{
  "last_sync_time": "2024-01-01T00:00:00Z"
}
```

#### Listar Backups
```bash
GET /backups?source_db=mysql&table_name=rooms
```

#### Listar Tablas DynamoDB
```bash
GET /dynamodb/tables
```

#### Obtener Items DynamoDB
```bash
GET /dynamodb/{table_name}/items?limit=100
```

### Ejemplos de Uso

#### Migración Completa
```bash
curl -X POST http://localhost:3006/migrate
```

#### Backup Manual
```bash
curl -X POST http://localhost:3006/backup
```

#### Verificar Estado
```bash
curl http://localhost:3006/health
```

#### Listar Backups Disponibles
```bash
curl "http://localhost:3006/backups?source_db=mysql"
```

## Programación Automática

El servicio incluye tareas programadas:

- **Backup diario**: 2:00 AM todos los días
- **Sincronización**: Cada 30 minutos

### Configurar Horarios

```python
# En config.py
BACKUP_SCHEDULE = "0 2 * * *"    # Diario a las 2 AM
SYNC_SCHEDULE = "*/30 * * * *"   # Cada 30 minutos
```

## Monitoreo y Logs

### Logs
- **Archivo**: `data_ingestion.log`
- **Nivel**: INFO, ERROR, DEBUG
- **Formato**: Timestamp, Logger, Level, Message

### Métricas
- Registros migrados por tabla
- Tiempo de migración
- Errores y reintentos
- Estado de conexiones AWS

### Reportes
Los reportes se generan automáticamente en S3:
```json
{
  "migration_timestamp": "2024-01-01T12:00:00Z",
  "record_counts": {
    "mysql": {"rooms": 100, "seats": 1000},
    "postgresql": {"users": 50, "reservations": 200},
    "mongodb": {"movies": 150, "genres": 10}
  },
  "total_records_migrated": 1510,
  "migration_status": "SUCCESS"
}
```

## Solución de Problemas

### Errores Comunes

#### 1. Credenciales AWS
```
Error: Credenciales de AWS no encontradas
```
**Solución**: Verificar `AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY`

#### 2. Bucket S3 no existe
```
Error: NoSuchBucket
```
**Solución**: Crear bucket con `python scripts/setup_aws_resources.py`

#### 3. Tablas DynamoDB
```
Error: ResourceNotFoundException
```
**Solución**: Ejecutar setup de tablas

#### 4. Conexión a Base de Datos
```
Error: Connection refused
```
**Solución**: Verificar que las bases de datos estén ejecutándose

### Debugging

```bash
# Habilitar logs detallados
export LOG_LEVEL=DEBUG
python main.py --mode api

# Verificar conexiones AWS
curl http://localhost:3006/health

# Probar migración de una tabla específica
curl -X POST http://localhost:3006/sync/rooms
```

## Integración con Microservicios

El servicio se integra con el sistema existente:

1. **Docker Compose**: Incluido en `docker-compose.yml`
2. **Red**: Conectado a la red `cinema_network`
3. **Variables**: Configurado para usar los mismos nombres de servicio
4. **Puerto**: 3006 (no conflictivo con otros servicios)

### Endpoints de Integración

```bash
# Desde Gateway API
curl -X POST http://data-ingestion-service:3006/migrate

# Desde Analytics API
curl http://data-ingestion-service:3006/dynamodb/tables
```

## Escalabilidad

### Procesamiento en Lotes
- **Tamaño por defecto**: 1000 registros
- **Configurable**: Variable `BATCH_SIZE`
- **Memoria eficiente**: Procesamiento streaming

### Manejo de Errores
- **Reintentos**: 3 intentos por defecto
- **Delay**: 5 segundos entre reintentos
- **Fallback**: Continuar con otros lotes si uno falla

### Optimizaciones
- **Conexiones pool**: Reutilización de conexiones DB
- **Compresión**: Datos comprimidos en S3
- **Índices**: Índices optimizados en DynamoDB

## Seguridad

### Encriptación
- **S3**: Encriptación AES-256 por defecto
- **DynamoDB**: Encriptación en tránsito y reposo
- **RDS**: SSL/TLS para conexiones

### Acceso
- **IAM**: Principio de menor privilegio
- **VPC**: Aislamiento de red (opcional)
- **Secrets**: Variables de entorno para credenciales

### Auditoría
- **CloudTrail**: Logs de API AWS
- **S3 Access Logs**: Monitoreo de accesos
- **DynamoDB**: Métricas de CloudWatch

## Costos Estimados

### S3
- **Almacenamiento**: ~$0.023/GB/mes
- **Requests**: ~$0.0004/1000 requests
- **Transfer**: Primeros 1GB gratis

### DynamoDB
- **Pay-per-request**: ~$1.25/millón requests
- **Almacenamiento**: ~$0.25/GB/mes

### RDS (Opcional)
- **db.t3.micro**: ~$15/mes
- **Almacenamiento**: ~$0.115/GB/mes

## Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.
