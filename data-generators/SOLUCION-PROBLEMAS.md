# 🚨 SOLUCIÓN RÁPIDA DE PROBLEMAS

## 🔥 **Errores Más Comunes y Sus Soluciones**

### ❌ **Error: Table 'cinema_rooms.seats' doesn't exist**
```
✅ SOLUCIÓN: Los scripts ahora crean las tablas automáticamente
✅ Si persiste: Reinicia MySQL con Docker
```
```bash
docker-compose restart mysql
# Esperar 10 segundos
python mysql-data-generator.py
```

### ❌ **Error: relation "users" does not exist**
```
✅ SOLUCIÓN: Los scripts ahora crean las tablas automáticamente  
✅ Si persiste: Reinicia PostgreSQL con Docker
```
```bash
docker-compose restart postgresql
# Esperar 10 segundos  
python postgresql-data-generator.py
```

### ❌ **Error: Connection refused**
```
✅ SOLUCIÓN: Las bases de datos no están corriendo
```
```bash
# Iniciar todas las bases de datos
docker-compose up -d mongodb mysql postgresql

# Verificar que estén corriendo
docker-compose ps

# Si no aparecen, reiniciar Docker Desktop
```

### ❌ **Error: Access denied for user**
```
✅ SOLUCIÓN: Credenciales incorrectas
✅ Las credenciales correctas están en .env
```

**Credenciales Docker (por defecto):**
- **MySQL**: `cinema_user` / `cinema_password` en puerto `3307`
- **PostgreSQL**: `cinema_user` / `cinema_password` en puerto `5432`
- **MongoDB**: Sin credenciales en puerto `27017`

### ❌ **Error: Module not found (pymongo, psycopg2, etc.)**
```bash
✅ SOLUCIÓN: Instalar dependencias faltantes
pip install -r requirements.txt

# O individualmente:
pip install pymongo mysql-connector-python psycopg2-binary python-dotenv
npm install
```

---

## 🚀 **SOLUCIÓN COMPLETA PASO A PASO**

### **Paso 1: Limpiar Todo y Empezar de Cero**
```bash
# Detener y eliminar contenedores (CUIDADO: borra datos)
docker-compose down -v

# Iniciar solo las bases de datos
docker-compose up -d mongodb mysql postgresql

# Esperar 30 segundos que se inicialicen
timeout 30
```

### **Paso 2: Verificar Conexiones**
```bash
cd data-generators
python test-connections.py
```

**Si ve ✅ en las 3 bases de datos, continúa al Paso 3**  
**Si ve ❌, revisa los errores específicos arriba**

### **Paso 3: Instalar Dependencias**
```bash
npm install
pip install -r requirements.txt
```

### **Paso 4: Generar Datos**
```bash
# Automático (recomendado)
run-all-generators.bat

# O manual:
node mongodb-data-generator.js
python mysql-data-generator.py
python postgresql-data-generator.py
```

### **Paso 5: Verificar Resultados**
```bash
node verify-data.js
```

---

## 🔧 **Comandos de Diagnóstico**

### **Ver logs de bases de datos:**
```bash
docker-compose logs mongodb
docker-compose logs mysql  
docker-compose logs postgresql
```

### **Conectar manualmente a las bases:**
```bash
# MongoDB
mongosh mongodb://localhost:27017/cinema_movies

# MySQL  
mysql -h localhost -P 3307 -u cinema_user -p cinema_rooms

# PostgreSQL
psql -h localhost -p 5432 -U cinema_user -d cinema_reservations
```

### **Verificar puertos ocupados:**
```bash
# Windows
netstat -ano | findstr :3307
netstat -ano | findstr :5432
netstat -ano | findstr :27017

# Linux/Mac
lsof -i :3307
lsof -i :5432  
lsof -i :27017
```

---

## 🆘 **Si Nada Funciona**

### **Opción Nuclear: Resetear Todo** ⚠️
```bash
# 1. Detener todo Docker
docker-compose down -v
docker system prune -f

# 2. Reiniciar Docker Desktop

# 3. Empezar limpio
docker-compose up -d mongodb mysql postgresql

# 4. Esperar 1 minuto completo
timeout 60

# 5. Probar conexiones
cd data-generators  
python test-connections.py

# 6. Si todo está ✅, generar datos
run-all-generators.bat
```

### **Alternativa: Instalación Local**
Si Docker no funciona, instala las bases de datos localmente:

1. **MongoDB**: https://www.mongodb.com/try/download/community
2. **MySQL**: https://dev.mysql.com/downloads/mysql/
3. **PostgreSQL**: https://www.postgresql.org/download/

Luego edita `.env` con las credenciales locales.

---

## 📞 **¿Necesitas Ayuda?**

Si sigues teniendo problemas:

1. **Ejecuta el diagnóstico:**
   ```bash
   python test-connections.py
   ```

2. **Copia el output completo** del error

3. **Incluye tu configuración:**
   - Sistema operativo
   - Versión de Docker
   - Contenido de `.env`

4. **Verifica estos puntos:**
   - ¿Docker Desktop está corriendo?
   - ¿Los puertos 3307, 5432, 27017 están libres?
   - ¿Las credenciales en `.env` coinciden con `docker-compose.yml`?

¡El 99% de los problemas se resuelven con Docker restart o reinstalar dependencias! 🎯