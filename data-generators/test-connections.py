#!/usr/bin/env python3
"""
Script para probar las conexiones a las bases de datos antes de generar datos
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_mongodb():
    """Probar conexión a MongoDB"""
    try:
        from pymongo import MongoClient
        
        uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/cinema_movies')
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Ping para verificar conexión
        client.admin.command('ping')
        
        # Verificar base de datos
        db = client['cinema_movies']
        collections = db.list_collection_names()
        
        print("✅ MongoDB: Conexión exitosa")
        print(f"   URI: {uri}")
        print(f"   Colecciones existentes: {len(collections)}")
        if collections:
            print(f"   → {', '.join(collections[:3])}{'...' if len(collections) > 3 else ''}")
        
        client.close()
        return True
        
    except ImportError:
        print("❌ MongoDB: Falta instalar pymongo")
        print("   Ejecuta: pip install pymongo")
        return False
    except Exception as e:
        print(f"❌ MongoDB: Error de conexión - {e}")
        print("   💡 Verifica que MongoDB esté corriendo en puerto 27017")
        return False

def test_mysql():
    """Probar conexión a MySQL"""
    try:
        import mysql.connector
        
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3307)),
            'user': os.getenv('MYSQL_USER', 'cinema_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'cinema_password'),
            'database': os.getenv('MYSQL_DATABASE', 'cinema_rooms')
        }
        
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Verificar tablas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("✅ MySQL: Conexión exitosa")
        print(f"   Host: {config['host']}:{config['port']}")
        print(f"   Usuario: {config['user']}")
        print(f"   Base de datos: {config['database']}")
        print(f"   Tablas existentes: {len(tables)}")
        if tables:
            table_names = [table[0] for table in tables]
            print(f"   → {', '.join(table_names[:3])}{'...' if len(tables) > 3 else ''}")
        
        connection.close()
        return True
        
    except ImportError:
        print("❌ MySQL: Falta instalar mysql-connector-python")
        print("   Ejecuta: pip install mysql-connector-python")
        return False
    except Exception as e:
        print(f"❌ MySQL: Error de conexión - {e}")
        print(f"   💡 Verifica que MySQL esté corriendo en puerto {config['port']}")
        print(f"   💡 Credenciales: {config['user']}/{config['password']}")
        return False

def test_postgresql():
    """Probar conexión a PostgreSQL"""
    try:
        import psycopg2
        
        config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'cinema_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'cinema_password'),
            'database': os.getenv('POSTGRES_DATABASE', 'cinema_reservations')
        }
        
        connection = psycopg2.connect(**config)
        cursor = connection.cursor()
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print("✅ PostgreSQL: Conexión exitosa")
        print(f"   Host: {config['host']}:{config['port']}")
        print(f"   Usuario: {config['user']}")
        print(f"   Base de datos: {config['database']}")
        print(f"   Tablas existentes: {len(tables)}")
        if tables:
            table_names = [table[0] for table in tables]
            print(f"   → {', '.join(table_names[:3])}{'...' if len(tables) > 3 else ''}")
        
        connection.close()
        return True
        
    except ImportError:
        print("❌ PostgreSQL: Falta instalar psycopg2")
        print("   Ejecuta: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL: Error de conexión - {e}")
        print(f"   💡 Verifica que PostgreSQL esté corriendo en puerto {config['port']}")
        print(f"   💡 Credenciales: {config['user']}/{config['password']}")
        return False

def main():
    print("🔍 PROBANDO CONEXIONES A BASES DE DATOS")
    print("=" * 50)
    print()
    
    # Verificar archivo .env
    if not os.path.exists('.env'):
        print("⚠️  Archivo .env no encontrado")
        print("💡 Copia .env.example como .env y configura las credenciales")
        print()
    
    results = []
    
    print("🐘 Probando PostgreSQL...")
    results.append(test_postgresql())
    print()
    
    print("🐬 Probando MySQL...")
    results.append(test_mysql())
    print()
    
    print("🍃 Probando MongoDB...")
    results.append(test_mongodb())
    print()
    
    # Resumen
    print("=" * 50)
    successful = sum(results)
    total = len(results)
    
    if successful == total:
        print(f"🎉 ¡PERFECTO! {successful}/{total} bases de datos conectadas")
        print("✅ Puedes ejecutar los generadores de datos")
    else:
        print(f"⚠️  {successful}/{total} bases de datos conectadas")
        if successful == 0:
            print("❌ Ninguna base de datos está disponible")
            print("💡 Ejecuta: docker-compose up -d mongodb mysql postgresql")
        else:
            print("⚠️  Algunas bases de datos no están disponibles")
    
    print()
    print("🔧 Comandos útiles:")
    print("   • Iniciar con Docker: docker-compose up -d mongodb mysql postgresql")
    print("   • Ver estado: docker-compose ps")
    print("   • Ver logs: docker-compose logs [servicio]")
    
    return successful == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)