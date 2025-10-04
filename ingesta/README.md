# 🚀 Sistema de Ingesta de Datos a S3 - AWS Academy

Este sistema permite extraer datos de todas las bases de datos del proyecto (MySQL, PostgreSQL, MongoDB) y subirlos a S3 usando credenciales de AWS Academy.

## 📊 Bases de Datos Soportadas

| Base de Datos | API | Tablas/Colecciones | Descripción |
|---------------|-----|-------------------|-------------|
| **MySQL** | Rooms API | `rooms`, `seats`, `schedules` | Salas, asientos y horarios |
| **PostgreSQL** | Reservations API | `users`, `reservations`, `reserved_seats`, `payments` | Usuarios, reservas y pagos |
| **MongoDB** | Movies API | `movies`, `genres` | Películas y géneros |

## 📁 Estructura del Proyecto

```
ingesta/
├── mysql-rooms-api/
│   ├── script-ingesta-mysql.py
│   └── requirements.txt
├── postgresql-reservations-api/
│   ├── script-ingesta-postgresql.py
│   └── requirements.txt
├── mongodb-movies-api/
│   ├── script-ingesta-mongodb.py
│   └── requirements.txt
├── run-all-ingesta.py          # Script principal
├── run-all-ingesta.bat         # Para Windows
├── run-all-ingesta.sh          # Para Linux/Mac
└── README.md                   # Este archivo
```

## 🛠️ Configuración Inicial

### 1. Credenciales AWS Academy

Antes de ejecutar cualquier script, necesitas configurar las credenciales de AWS Academy:

```bash
# Opción 1: Variables de entorno (recomendado)
export AWS_ACCESS_KEY_ID="tu_access_key"
export AWS_SECRET_ACCESS_KEY="tu_secret_key"  
export AWS_SESSION_TOKEN="tu_session_token"
export AWS_DEFAULT_REGION="us-east-1"
```

```bash
# Opción 2: Archivo .env en cada carpeta
# Crea un archivo .env en cada subcarpeta con:
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_SESSION_TOKEN=tu_session_token
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=cinema-analytics-data
```

### 2. Configuración de Bases de Datos

Cada script necesita la configuración correspondiente:

#### MySQL (Rooms API)
```env
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_USER=cinema_user
MYSQL_PASSWORD=cinema_password
MYSQL_DATABASE=cinema_rooms
```

#### PostgreSQL (Reservations API)
```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DATABASE=cinema_reservations
```

#### MongoDB (Movies API)
```env
MONGODB_URI=mongodb://localhost:27017/cinema_movies
MONGODB_DATABASE=cinema_movies
```

### 3. Instalación de Dependencias

```bash
# Para cada subcarpeta, instalar dependencias:

# MySQL
cd mysql-rooms-api
pip install -r requirements.txt

# PostgreSQL  
cd ../postgresql-reservations-api
pip install -r requirements.txt

# MongoDB
cd ../mongodb-movies-api
pip install -r requirements.txt
```

## 🚀 Uso del Sistema

### Opción 1: Script Principal (Recomendado)

```bash
# Ejecutar menú interactivo
python run-all-ingesta.py

# O usar directamente desde Windows
run-all-ingesta.bat

# O desde Linux/Mac
./run-all-ingesta.sh
```

### Opción 2: Argumentos de Línea de Comandos

```bash
# Test rápido de todas las bases de datos
python run-all-ingesta.py test

# Ingesta completa de todas las bases de datos  
python run-all-ingesta.py full

# Ejecutar script individual
python run-all-ingesta.py mysql
python run-all-ingesta.py postgresql
python run-all-ingesta.py mongodb
```

### Opción 3: Scripts Individuales

```bash
# MySQL
cd mysql-rooms-api
python script-ingesta-mysql.py

# PostgreSQL
cd postgresql-reservations-api
python script-ingesta-postgresql.py

# MongoDB
cd mongodb-movies-api
python script-ingesta-mongodb.py
```

## 📋 Menú Interactivo

El script principal ofrece las siguientes opciones:

1. **🧪 Test rápido**: Extrae una pequeña muestra de datos de cada base
2. **📦 Ingesta completa**: Extrae todos los datos de todas las bases
3. **🎯 Script individual**: Ejecuta solo uno de los scripts
4. **ℹ️ Información**: Muestra el estado de todos los scripts
5. **🚪 Salir**: Cierra el programa

## 📂 Estructura de Archivos en S3

Los datos se organizan en S3 de la siguiente manera:

```
s3://cinema-analytics-data/
├── mysql-data/
│   ├── rooms/
│   │   ├── rooms_20231003_143022.csv
│   │   ├── rooms_20231003_143022.json
│   │   ├── seats_20231003_143022.csv
│   │   └── schedules_20231003_143022.csv
│   └── test/
├── postgresql-data/
│   ├── reservations/
│   │   ├── users_20231003_143022.csv
│   │   ├── users_20231003_143022.json
│   │   ├── reservations_20231003_143022.csv
│   │   └── payments_20231003_143022.csv
│   └── test/
├── mongodb-data/
│   ├── movies/
│   │   ├── movies_20231003_143022.csv
│   │   ├── movies_20231003_143022.json
│   │   ├── genres_20231003_143022.csv
│   │   └── metadata_20231003_143022.json
│   └── test/
```

## 🔧 Solución de Problemas

### Error de Credenciales AWS
```
❌ Faltan credenciales AWS Academy
```
**Solución**: Copia las 3 líneas de credenciales de AWS Academy y ejecútalas en tu terminal.

### Error de Conexión a Base de Datos
```
❌ Error conectando a [MySQL/PostgreSQL/MongoDB]
```
**Solución**: 
- Verifica que la base de datos esté ejecutándose
- Revisa la configuración en el archivo `.env`
- Comprueba los puertos y credenciales

### Error de Permisos S3
```
❌ Error creando bucket / subiendo archivo
```
**Solución**:
- Verifica que las credenciales AWS Academy sean válidas
- Asegúrate de que el Session Token no haya expirado
- Comprueba que tienes permisos de escritura en S3

### Script No Encontrado
```
❌ Script no encontrado
```
**Solución**:
- Verifica que estés en la carpeta correcta (`ingesta/`)
- Asegúrate de que todos los archivos se hayan descargado correctamente

## 🔒 Seguridad y Mejores Prácticas

1. **Credenciales**: Nunca subas credenciales a repositorios públicos
2. **Session Token**: Las credenciales de AWS Academy expiran, renuévalas regularmente
3. **Bucket**: Usa un bucket único para evitar conflictos
4. **Logs**: Revisa los logs para detectar problemas tempranamente
5. **Backups**: Los datos en S3 sirven como respaldo de tus bases de datos

## 📈 Monitoreo y Logs

Cada script genera logs detallados:

- ✅ **Éxito**: Operaciones completadas correctamente
- ⚠️ **Advertencia**: Situaciones que requieren atención
- ❌ **Error**: Problemas que impiden la ejecución
- 📊 **Info**: Información general sobre el proceso

## 🆘 Soporte

Si encuentras problemas:

1. Revisa los logs de error
2. Verifica la configuración de credenciales
3. Comprueba que las bases de datos estén accesibles
4. Revisa la conectividad a internet para S3

## 📝 Ejemplo de Ejecución Exitosa

```
🚀 Iniciando ingesta completa de todas las bases de datos...

============================================================
🔄 Procesando: MySQL (Rooms API)
📋 Datos: Salas, asientos y horarios  
============================================================
✅ Conexión exitosa a MySQL
📊 Datos extraídos de rooms: 5 registros
📊 Datos extraídos de seats: 120 registros
📊 Datos extraídos de schedules: 25 registros
✅ MySQL (Rooms API) - Completado en 0:00:15

============================================================
🔄 Procesando: PostgreSQL (Reservations API)
📋 Datos: Usuarios, reservas y pagos
============================================================
✅ Conexión exitosa a PostgreSQL
📊 Datos extraídos de users: 50 registros
📊 Datos extraídos de reservations: 200 registros
✅ PostgreSQL (Reservations API) - Completado en 0:00:12

============================================================
🔄 Procesando: MongoDB (Movies API)  
📋 Datos: Películas y géneros
============================================================
✅ Conexión exitosa a MongoDB
📊 Datos extraídos de movies: 150 documentos
📊 Datos extraídos de genres: 15 documentos
✅ MongoDB (Movies API) - Completado en 0:00:08

============================================================
📊 RESUMEN DE INGESTA
============================================================
✅ EXITOSO   | MySQL (Rooms API)             | 0:00:15
✅ EXITOSO   | PostgreSQL (Reservations API) | 0:00:12  
✅ EXITOSO   | MongoDB (Movies API)          | 0:00:08

📈 Resultados: 3/3 scripts exitosos
⏱️ Tiempo total: 0:00:35

🎉 ¡INGESTA COMPLETA EXITOSA!
🚀 Todas las bases de datos han sido subidas a S3
```

## 🎯 Próximos Pasos

Una vez que hayas ejecutado la ingesta exitosamente, puedes:

1. **Verificar en S3**: Revisa que los archivos estén en tu bucket
2. **Analytics**: Usar los datos para análisis con herramientas como AWS Athena
3. **Automatización**: Programar ejecuciones regulares con cron o Task Scheduler
4. **Monitoring**: Configurar alertas para monitorear el estado de las ingestas