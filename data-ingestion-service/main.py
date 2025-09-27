#!/usr/bin/env python3
"""
Servicio de Ingesta de Datos para AWS
Sistema de migración y sincronización de datos del cine a servicios de AWS
"""

import logging
import argparse
import schedule
import time
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from aws_clients import aws_manager
from data_migration import DataMigrationService
from s3_service import S3Service
from dynamodb_service import DynamoDBService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_ingestion.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Inicializar servicios
migration_service = DataMigrationService()
s3_service = S3Service()
dynamodb_service = DynamoDBService()

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    try:
        # Probar conexiones AWS
        aws_status = aws_manager.test_connections()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'aws_connections': aws_status
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/migrate', methods=['POST'])
def migrate_data():
    """Endpoint para migrar todos los datos a AWS"""
    try:
        logger.info("Iniciando migración manual de datos")
        
        # Ejecutar migración completa
        success = migration_service.migrate_all_data()
        
        if success:
            return jsonify({
                'message': 'Migración completada exitosamente',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'message': 'Error durante la migración',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error en migración: {e}")
        return jsonify({
            'message': f'Error en migración: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/backup', methods=['POST'])
def backup_data():
    """Endpoint para crear backup a S3"""
    try:
        logger.info("Iniciando backup manual de datos")
        
        # Obtener datos de todas las bases de datos
        db_manager = migration_service.db_manager
        db_manager.connect_all()
        all_data = db_manager.fetch_all_data()
        db_manager.disconnect_all()
        
        # Subir backup a S3
        success = migration_service.migrate_to_s3(all_data)
        
        if success:
            return jsonify({
                'message': 'Backup completado exitosamente',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'message': 'Error durante el backup',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error en backup: {e}")
        return jsonify({
            'message': f'Error en backup: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/sync/<table_name>', methods=['POST'])
def incremental_sync(table_name):
    """Endpoint para sincronización incremental"""
    try:
        last_sync_time = request.json.get('last_sync_time') if request.json else None
        
        logger.info(f"Iniciando sincronización incremental para {table_name}")
        
        success = migration_service.incremental_sync(table_name, last_sync_time)
        
        if success:
            return jsonify({
                'message': f'Sincronización de {table_name} completada exitosamente',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'message': f'Error en sincronización de {table_name}',
                'timestamp': datetime.now().isoformat()
            }), 500
            
    except Exception as e:
        logger.error(f"Error en sincronización: {e}")
        return jsonify({
            'message': f'Error en sincronización: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/backups', methods=['GET'])
def list_backups():
    """Endpoint para listar backups disponibles"""
    try:
        source_db = request.args.get('source_db')
        table_name = request.args.get('table_name')
        
        backups = s3_service.list_backups(source_db, table_name)
        
        return jsonify({
            'backups': backups,
            'count': len(backups)
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando backups: {e}")
        return jsonify({
            'message': f'Error listando backups: {str(e)}'
        }), 500

@app.route('/dynamodb/tables', methods=['GET'])
def list_dynamodb_tables():
    """Endpoint para listar tablas de DynamoDB"""
    try:
        tables = dynamodb_service.setup_cinema_tables()
        
        table_info = {}
        for name, table in tables.items():
            table_info[name] = {
                'table_name': table.table_name,
                'item_count': table.item_count,
                'table_status': table.table_status
            }
        
        return jsonify({
            'tables': table_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error listando tablas DynamoDB: {e}")
        return jsonify({
            'message': f'Error listando tablas: {str(e)}'
        }), 500

@app.route('/dynamodb/<table_name>/items', methods=['GET'])
def get_dynamodb_items(table_name):
    """Endpoint para obtener items de una tabla DynamoDB"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        items = dynamodb_service.scan_table(table_name, limit=limit)
        
        return jsonify({
            'table_name': table_name,
            'items': items,
            'count': len(items)
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo items de {table_name}: {e}")
        return jsonify({
            'message': f'Error obteniendo items: {str(e)}'
        }), 500

def scheduled_backup():
    """Función para backup programado"""
    logger.info("Ejecutando backup programado")
    try:
        # Obtener datos y hacer backup
        db_manager = migration_service.db_manager
        db_manager.connect_all()
        all_data = db_manager.fetch_all_data()
        db_manager.disconnect_all()
        
        migration_service.migrate_to_s3(all_data)
        logger.info("Backup programado completado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en backup programado: {e}")

def scheduled_sync():
    """Función para sincronización programada"""
    logger.info("Ejecutando sincronización programada")
    try:
        # Implementar lógica de sincronización incremental
        # Por ahora, hacer un backup completo
        scheduled_backup()
        logger.info("Sincronización programada completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error en sincronización programada: {e}")

def setup_scheduler():
    """Configurar tareas programadas"""
    try:
        # Backup diario
        schedule.every().day.at("02:00").do(scheduled_backup)
        
        # Sincronización cada 30 minutos
        schedule.every(30).minutes.do(scheduled_sync)
        
        logger.info("Scheduler configurado exitosamente")
        
    except Exception as e:
        logger.error(f"Error configurando scheduler: {e}")

def run_scheduler():
    """Ejecutar scheduler en loop separado"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar cada minuto

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Servicio de Ingesta de Datos AWS')
    parser.add_argument('--mode', choices=['api', 'migrate', 'backup', 'scheduler'], 
                       default='api', help='Modo de ejecución')
    parser.add_argument('--port', type=int, default=3006, help='Puerto para la API')
    
    args = parser.parse_args()
    
    if args.mode == 'migrate':
        logger.info("Ejecutando migración completa")
        success = migration_service.migrate_all_data()
        if success:
            logger.info("Migración completada exitosamente")
        else:
            logger.error("Error en la migración")
            
    elif args.mode == 'backup':
        logger.info("Ejecutando backup")
        db_manager = migration_service.db_manager
        db_manager.connect_all()
        all_data = db_manager.fetch_all_data()
        db_manager.disconnect_all()
        
        success = migration_service.migrate_to_s3(all_data)
        if success:
            logger.info("Backup completado exitosamente")
        else:
            logger.error("Error en el backup")
            
    elif args.mode == 'scheduler':
        logger.info("Ejecutando scheduler")
        setup_scheduler()
        run_scheduler()
        
    else:  # api mode
        logger.info("Iniciando API de ingesta de datos")
        
        # Configurar scheduler en background
        setup_scheduler()
        
        # Iniciar servidor Flask
        app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()
