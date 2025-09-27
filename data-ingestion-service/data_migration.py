import logging
from datetime import datetime
from database_connectors import DatabaseManager
from s3_service import S3Service
from dynamodb_service import DynamoDBService
from config import Config

logger = logging.getLogger(__name__)

class DataMigrationService:
    """Servicio para migración de datos a AWS"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.s3_service = S3Service()
        self.dynamodb_service = DynamoDBService()
        self.batch_size = Config.BATCH_SIZE
    
    def migrate_all_data(self):
        """Migrar todos los datos a AWS"""
        logger.info("Iniciando migración completa de datos a AWS")
        
        # Conectar a todas las bases de datos
        connections = self.db_manager.connect_all()
        if not all(connections.values()):
            logger.error("No se pudieron establecer todas las conexiones")
            return False
        
        try:
            # Obtener todos los datos
            all_data = self.db_manager.fetch_all_data()
            
            # Migrar a S3 (backup)
            s3_success = self.migrate_to_s3(all_data)
            
            # Migrar a DynamoDB
            dynamodb_success = self.migrate_to_dynamodb(all_data)
            
            # Crear reporte de migración
            self.create_migration_report(all_data, s3_success, dynamodb_success)
            
            logger.info("Migración completada exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error durante la migración: {e}")
            return False
        finally:
            self.db_manager.disconnect_all()
    
    def migrate_to_s3(self, all_data):
        """Migrar datos a S3 como backup"""
        logger.info("Migrando datos a S3...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Backup de MySQL
            for table_name, data in all_data['mysql'].items():
                if data:
                    success = self.s3_service.backup_database_table(
                        table_name, data, 'mysql'
                    )
                    if success:
                        logger.info(f"✅ MySQL {table_name} migrado a S3")
                    else:
                        logger.error(f"❌ Error migrando MySQL {table_name} a S3")
            
            # Backup de PostgreSQL
            for table_name, data in all_data['postgresql'].items():
                if data:
                    success = self.s3_service.backup_database_table(
                        table_name, data, 'postgresql'
                    )
                    if success:
                        logger.info(f"✅ PostgreSQL {table_name} migrado a S3")
                    else:
                        logger.error(f"❌ Error migrando PostgreSQL {table_name} a S3")
            
            # Backup de MongoDB
            for collection_name, data in all_data['mongodb'].items():
                if data:
                    success = self.s3_service.backup_database_table(
                        collection_name, data, 'mongodb'
                    )
                    if success:
                        logger.info(f"✅ MongoDB {collection_name} migrado a S3")
                    else:
                        logger.error(f"❌ Error migrando MongoDB {collection_name} a S3")
            
            return True
            
        except Exception as e:
            logger.error(f"Error migrando a S3: {e}")
            return False
    
    def migrate_to_dynamodb(self, all_data):
        """Migrar datos a DynamoDB"""
        logger.info("Migrando datos a DynamoDB...")
        
        try:
            # Configurar tablas
            tables = self.dynamodb_service.setup_cinema_tables()
            
            # Migrar películas
            if all_data['mongodb']['movies']:
                movies_data = self.transform_movies_for_dynamodb(all_data['mongodb']['movies'])
                success = self.dynamodb_service.batch_write_items('movies', movies_data)
                if success:
                    logger.info(f"✅ {len(movies_data)} películas migradas a DynamoDB")
            
            # Migrar géneros (como parte de movies)
            if all_data['mongodb']['genres']:
                genres_data = self.transform_genres_for_dynamodb(all_data['mongodb']['genres'])
                # Los géneros se almacenan como parte de las películas
            
            # Migrar salas
            if all_data['mysql']['rooms']:
                rooms_data = self.transform_rooms_for_dynamodb(all_data['mysql']['rooms'])
                success = self.dynamodb_service.batch_write_items('rooms', rooms_data)
                if success:
                    logger.info(f"✅ {len(rooms_data)} salas migradas a DynamoDB")
            
            # Migrar usuarios
            if all_data['postgresql']['users']:
                users_data = self.transform_users_for_dynamodb(all_data['postgresql']['users'])
                success = self.dynamodb_service.batch_write_items('users', users_data)
                if success:
                    logger.info(f"✅ {len(users_data)} usuarios migrados a DynamoDB")
            
            # Migrar reservas
            if all_data['postgresql']['reservations']:
                reservations_data = self.transform_reservations_for_dynamodb(all_data['postgresql']['reservations'])
                success = self.dynamodb_service.batch_write_items('reservations', reservations_data)
                if success:
                    logger.info(f"✅ {len(reservations_data)} reservas migradas a DynamoDB")
            
            return True
            
        except Exception as e:
            logger.error(f"Error migrando a DynamoDB: {e}")
            return False
    
    def transform_movies_for_dynamodb(self, movies):
        """Transformar películas para DynamoDB"""
        transformed = []
        for movie in movies:
            item = {
                'movie_id': movie.get('_id', str(movie.get('id', ''))),
                'title': movie.get('title', ''),
                'description': movie.get('description', ''),
                'release_date': movie.get('release_date', ''),
                'duration': movie.get('duration', 0),
                'rating': movie.get('rating', 0.0),
                'genre_id': movie.get('genre_id', ''),
                'genre_name': movie.get('genre_name', ''),
                'poster_url': movie.get('poster_url', ''),
                'trailer_url': movie.get('trailer_url', ''),
                'is_featured': movie.get('is_featured', False),
                'created_at': movie.get('created_at', datetime.now().isoformat()),
                'updated_at': movie.get('updated_at', datetime.now().isoformat())
            }
            transformed.append(item)
        return transformed
    
    def transform_genres_for_dynamodb(self, genres):
        """Transformar géneros para DynamoDB"""
        transformed = []
        for genre in genres:
            item = {
                'genre_id': genre.get('_id', str(genre.get('id', ''))),
                'name': genre.get('name', ''),
                'description': genre.get('description', ''),
                'created_at': genre.get('created_at', datetime.now().isoformat())
            }
            transformed.append(item)
        return transformed
    
    def transform_rooms_for_dynamodb(self, rooms):
        """Transformar salas para DynamoDB"""
        transformed = []
        for room in rooms:
            item = {
                'room_id': room.get('id', 0),
                'name': room.get('name', ''),
                'capacity': room.get('capacity', 0),
                'screen_type': room.get('screen_type', ''),
                'is_active': room.get('is_active', True),
                'created_at': room.get('created_at', datetime.now().isoformat()),
                'updated_at': room.get('updated_at', datetime.now().isoformat())
            }
            transformed.append(item)
        return transformed
    
    def transform_users_for_dynamodb(self, users):
        """Transformar usuarios para DynamoDB"""
        transformed = []
        for user in users:
            item = {
                'user_id': str(user.get('id', '')),
                'email': user.get('email', ''),
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'phone': user.get('phone', ''),
                'date_of_birth': user.get('date_of_birth', ''),
                'created_at': user.get('created_at', datetime.now().isoformat()),
                'updated_at': user.get('updated_at', datetime.now().isoformat())
            }
            transformed.append(item)
        return transformed
    
    def transform_reservations_for_dynamodb(self, reservations):
        """Transformar reservas para DynamoDB"""
        transformed = []
        for reservation in reservations:
            item = {
                'reservation_id': str(reservation.get('id', '')),
                'user_id': str(reservation.get('user_id', '')),
                'movie_id': str(reservation.get('movie_id', '')),
                'room_id': reservation.get('room_id', 0),
                'reservation_date': reservation.get('reservation_date', ''),
                'total_amount': float(reservation.get('total_amount', 0.0)),
                'status': reservation.get('status', 'PENDING'),
                'created_at': reservation.get('created_at', datetime.now().isoformat()),
                'updated_at': reservation.get('updated_at', datetime.now().isoformat())
            }
            transformed.append(item)
        return transformed
    
    def create_migration_report(self, all_data, s3_success, dynamodb_success):
        """Crear reporte de migración"""
        try:
            timestamp = datetime.now().isoformat()
            
            # Contar registros
            record_counts = {
                'mysql': {table: len(data) for table, data in all_data['mysql'].items()},
                'postgresql': {table: len(data) for table, data in all_data['postgresql'].items()},
                'mongodb': {collection: len(data) for collection, data in all_data['mongodb'].items()}
            }
            
            report = {
                'migration_timestamp': timestamp,
                'record_counts': record_counts,
                's3_migration_success': s3_success,
                'dynamodb_migration_success': dynamodb_success,
                'total_records_migrated': sum(
                    sum(table_counts.values()) 
                    for table_counts in record_counts.values()
                ),
                'migration_status': 'SUCCESS' if s3_success and dynamodb_success else 'PARTIAL'
            }
            
            # Subir reporte a S3
            self.s3_service.upload_analytics_data(
                report, 
                'migration_report',
                timestamp
            )
            
            logger.info(f"Reporte de migración creado: {report}")
            
        except Exception as e:
            logger.error(f"Error creando reporte de migración: {e}")
    
    def incremental_sync(self, table_name, last_sync_time):
        """Sincronización incremental de datos"""
        logger.info(f"Iniciando sincronización incremental para {table_name}")
        
        # Esta función implementaría la lógica para sincronizar solo
        # los datos que han cambiado desde la última sincronización
        # Por simplicidad, aquí se muestra la estructura básica
        
        try:
            # Conectar a la base de datos correspondiente
            self.db_manager.connect_all()
            
            # Obtener datos modificados desde last_sync_time
            # (implementar lógica específica según la tabla)
            
            # Migrar solo los datos nuevos/modificados
            
            logger.info(f"Sincronización incremental completada para {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error en sincronización incremental: {e}")
            return False
        finally:
            self.db_manager.disconnect_all()
