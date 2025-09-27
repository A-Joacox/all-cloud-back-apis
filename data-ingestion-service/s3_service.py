import json
import pandas as pd
import logging
from datetime import datetime
from io import StringIO
from botocore.exceptions import ClientError
from aws_clients import aws_manager
from config import Config

logger = logging.getLogger(__name__)

class S3Service:
    """Servicio para operaciones con Amazon S3"""
    
    def __init__(self):
        self.s3_client = aws_manager.get_s3_client()
        self.bucket_name = Config.S3_BUCKET_NAME
    
    def upload_json_data(self, data, key, metadata=None):
        """Subir datos JSON a S3"""
        try:
            json_data = json.dumps(data, default=str, ensure_ascii=False)
            
            extra_args = {
                'ContentType': 'application/json',
                'ServerSideEncryption': 'AES256'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data,
                **extra_args
            )
            
            logger.info(f"Datos JSON subidos exitosamente a s3://{self.bucket_name}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error subiendo JSON a S3: {e}")
            return False
    
    def upload_csv_data(self, df, key, metadata=None):
        """Subir DataFrame como CSV a S3"""
        try:
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            
            extra_args = {
                'ContentType': 'text/csv',
                'ServerSideEncryption': 'AES256'
            }
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=csv_buffer.getvalue(),
                **extra_args
            )
            
            logger.info(f"CSV subido exitosamente a s3://{self.bucket_name}/{key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error subiendo CSV a S3: {e}")
            return False
    
    def backup_database_table(self, table_name, data, source_db):
        """Crear backup de una tabla de base de datos"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        key = f"{Config.S3_BACKUP_FOLDER}/{source_db}/{table_name}/{timestamp}_{table_name}.json"
        
        metadata = {
            'table_name': table_name,
            'source_database': source_db,
            'backup_timestamp': timestamp,
            'record_count': str(len(data))
        }
        
        return self.upload_json_data(data, key, metadata)
    
    def upload_analytics_data(self, analytics_data, report_type, timestamp=None):
        """Subir datos de analytics a S3"""
        if not timestamp:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        key = f"{Config.S3_ANALYTICS_FOLDER}/{report_type}/{timestamp}_{report_type}.json"
        
        metadata = {
            'report_type': report_type,
            'generated_timestamp': timestamp,
            'data_source': 'cinema_analytics'
        }
        
        return self.upload_json_data(analytics_data, key, metadata)
    
    def download_data(self, key):
        """Descargar datos de S3"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read().decode('utf-8')
            
            # Intentar parsear como JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Si no es JSON, devolver como texto
                return content
                
        except ClientError as e:
            logger.error(f"Error descargando datos de S3: {e}")
            return None
    
    def list_backups(self, source_db=None, table_name=None):
        """Listar backups disponibles"""
        try:
            prefix = Config.S3_BACKUP_FOLDER
            if source_db:
                prefix += f"/{source_db}"
                if table_name:
                    prefix += f"/{table_name}"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            backups = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    backups.append({
                        'key': obj['Key'],
                        'last_modified': obj['LastModified'],
                        'size': obj['Size']
                    })
            
            return backups
            
        except ClientError as e:
            logger.error(f"Error listando backups: {e}")
            return []
    
    def create_lifecycle_policy(self):
        """Crear política de lifecycle para backups"""
        try:
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'CinemaBackupsLifecycle',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': Config.S3_BACKUP_FOLDER},
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'STANDARD_IA'
                            },
                            {
                                'Days': 90,
                                'StorageClass': 'GLACIER'
                            }
                        ],
                        'Expiration': {
                            'Days': 365
                        }
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            
            logger.info("Política de lifecycle creada exitosamente")
            return True
            
        except ClientError as e:
            logger.error(f"Error creando política de lifecycle: {e}")
            return False
