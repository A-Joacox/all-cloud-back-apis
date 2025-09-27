import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from config import Config

logger = logging.getLogger(__name__)

class AWSClientManager:
    """Manager para todos los clientes de AWS"""
    
    def __init__(self):
        self._s3_client = None
        self._dynamodb_client = None
        self._dynamodb_resource = None
        self._rds_client = None
        self._session = None
        
    def get_session(self):
        """Crear sesión de AWS"""
        if not self._session:
            try:
                self._session = boto3.Session(
                    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                    region_name=Config.AWS_REGION
                )
                logger.info("Sesión de AWS creada exitosamente")
            except NoCredentialsError:
                logger.error("Credenciales de AWS no encontradas")
                raise
            except Exception as e:
                logger.error(f"Error creando sesión de AWS: {e}")
                raise
        return self._session
    
    def get_s3_client(self):
        """Obtener cliente de S3"""
        if not self._s3_client:
            session = self.get_session()
            self._s3_client = session.client('s3')
            logger.info("Cliente S3 creado exitosamente")
        return self._s3_client
    
    def get_dynamodb_client(self):
        """Obtener cliente de DynamoDB"""
        if not self._dynamodb_client:
            session = self.get_session()
            self._dynamodb_client = session.client('dynamodb')
            logger.info("Cliente DynamoDB creado exitosamente")
        return self._dynamodb_client
    
    def get_dynamodb_resource(self):
        """Obtener recurso de DynamoDB"""
        if not self._dynamodb_resource:
            session = self.get_session()
            self._dynamodb_resource = session.resource('dynamodb')
            logger.info("Recurso DynamoDB creado exitosamente")
        return self._dynamodb_resource
    
    def get_rds_client(self):
        """Obtener cliente de RDS"""
        if not self._rds_client:
            session = self.get_session()
            self._rds_client = session.client('rds')
            logger.info("Cliente RDS creado exitosamente")
        return self._rds_client
    
    def test_connections(self):
        """Probar todas las conexiones de AWS"""
        results = {}
        
        # Test S3
        try:
            s3_client = self.get_s3_client()
            s3_client.head_bucket(Bucket=Config.S3_BUCKET_NAME)
            results['s3'] = {'status': 'success', 'message': 'S3 conectado exitosamente'}
        except ClientError as e:
            results['s3'] = {'status': 'error', 'message': f'Error S3: {e}'}
        
        # Test DynamoDB
        try:
            dynamodb_client = self.get_dynamodb_client()
            dynamodb_client.list_tables()
            results['dynamodb'] = {'status': 'success', 'message': 'DynamoDB conectado exitosamente'}
        except ClientError as e:
            results['dynamodb'] = {'status': 'error', 'message': f'Error DynamoDB: {e}'}
        
        # Test RDS (si está configurado)
        if Config.RDS_ENDPOINT:
            try:
                rds_client = self.get_rds_client()
                rds_client.describe_db_instances()
                results['rds'] = {'status': 'success', 'message': 'RDS conectado exitosamente'}
            except ClientError as e:
                results['rds'] = {'status': 'error', 'message': f'Error RDS: {e}'}
        
        return results

# Instancia global del manager
aws_manager = AWSClientManager()
