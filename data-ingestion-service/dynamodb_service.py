import json
import logging
from datetime import datetime
from decimal import Decimal
from botocore.exceptions import ClientError
from aws_clients import aws_manager
from config import Config

logger = logging.getLogger(__name__)

class DynamoDBService:
    """Servicio para operaciones con Amazon DynamoDB"""
    
    def __init__(self):
        self.dynamodb_resource = aws_manager.get_dynamodb_resource()
        self.dynamodb_client = aws_manager.get_dynamodb_client()
        self.tables = Config.DYNAMODB_TABLES
    
    def decimal_default(self, obj):
        """Convertir Decimal a float para JSON serialization"""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError
    
    def create_table_if_not_exists(self, table_name, key_schema, attribute_definitions, 
                                   provisioned_throughput=None, global_secondary_indexes=None):
        """Crear tabla si no existe"""
        try:
            table = self.dynamodb_resource.Table(table_name)
            table.load()
            logger.info(f"Tabla {table_name} ya existe")
            return table
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                try:
                    create_params = {
                        'TableName': table_name,
                        'KeySchema': key_schema,
                        'AttributeDefinitions': attribute_definitions
                    }
                    
                    if provisioned_throughput:
                        create_params['BillingMode'] = 'PROVISIONED'
                        create_params['ProvisionedThroughput'] = provisioned_throughput
                    else:
                        create_params['BillingMode'] = 'PAY_PER_REQUEST'
                    
                    if global_secondary_indexes:
                        create_params['GlobalSecondaryIndexes'] = global_secondary_indexes
                    
                    table = self.dynamodb_resource.create_table(**create_params)
                    logger.info(f"Tabla {table_name} creada exitosamente")
                    table.wait_until_exists()
                    return table
                    
                except ClientError as create_error:
                    logger.error(f"Error creando tabla {table_name}: {create_error}")
                    raise
            else:
                logger.error(f"Error verificando tabla {table_name}: {e}")
                raise
    
    def setup_cinema_tables(self):
        """Configurar todas las tablas del cine"""
        tables_config = {
            'movies': {
                'key_schema': [
                    {'AttributeName': 'movie_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'movie_id', 'AttributeType': 'S'},
                    {'AttributeName': 'genre_id', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': [
                    {
                        'IndexName': 'GenreIndex',
                        'KeySchema': [{'AttributeName': 'genre_id', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },
            'rooms': {
                'key_schema': [
                    {'AttributeName': 'room_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'room_id', 'AttributeType': 'N'},
                    {'AttributeName': 'screen_type', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': [
                    {
                        'IndexName': 'ScreenTypeIndex',
                        'KeySchema': [{'AttributeName': 'screen_type', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },
            'reservations': {
                'key_schema': [
                    {'AttributeName': 'reservation_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'reservation_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'movie_id', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': [
                    {
                        'IndexName': 'UserIndex',
                        'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'MovieIndex',
                        'KeySchema': [{'AttributeName': 'movie_id', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },
            'users': {
                'key_schema': [
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                'global_secondary_indexes': [
                    {
                        'IndexName': 'EmailIndex',
                        'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            }
        }
        
        created_tables = {}
        
        for table_name, config in tables_config.items():
            full_table_name = self.tables[table_name]
            try:
                table = self.create_table_if_not_exists(
                    full_table_name,
                    config['key_schema'],
                    config['attribute_definitions'],
                    global_secondary_indexes=config.get('global_secondary_indexes')
                )
                created_tables[table_name] = table
            except Exception as e:
                logger.error(f"Error configurando tabla {table_name}: {e}")
        
        return created_tables
    
    def batch_write_items(self, table_name, items):
        """Escribir múltiples items en lote"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            
            logger.info(f"{len(items)} items escritos exitosamente en {table_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error escribiendo items en {table_name}: {e}")
            return False
    
    def put_item(self, table_name, item):
        """Insertar un item"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            table.put_item(Item=item)
            logger.info(f"Item insertado exitosamente en {table_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error insertando item en {table_name}: {e}")
            return False
    
    def get_item(self, table_name, key):
        """Obtener un item por clave"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            response = table.get_item(Key=key)
            
            if 'Item' in response:
                return response['Item']
            return None
            
        except ClientError as e:
            logger.error(f"Error obteniendo item de {table_name}: {e}")
            return None
    
    def query_items(self, table_name, key_condition_expression, 
                   filter_expression=None, index_name=None):
        """Consultar items"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            
            query_params = {
                'KeyConditionExpression': key_condition_expression
            }
            
            if filter_expression:
                query_params['FilterExpression'] = filter_expression
            
            if index_name:
                query_params['IndexName'] = index_name
            
            response = table.query(**query_params)
            return response['Items']
            
        except ClientError as e:
            logger.error(f"Error consultando items de {table_name}: {e}")
            return []
    
    def scan_table(self, table_name, filter_expression=None, limit=None):
        """Escanear toda la tabla"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            
            scan_params = {}
            if filter_expression:
                scan_params['FilterExpression'] = filter_expression
            if limit:
                scan_params['Limit'] = limit
            
            response = table.scan(**scan_params)
            return response['Items']
            
        except ClientError as e:
            logger.error(f"Error escaneando tabla {table_name}: {e}")
            return []
    
    def update_item(self, table_name, key, update_expression, 
                   expression_attribute_values=None, expression_attribute_names=None):
        """Actualizar un item"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            
            update_params = {
                'Key': key,
                'UpdateExpression': update_expression
            }
            
            if expression_attribute_values:
                update_params['ExpressionAttributeValues'] = expression_attribute_values
            if expression_attribute_names:
                update_params['ExpressionAttributeNames'] = expression_attribute_names
            
            table.update_item(**update_params)
            logger.info(f"Item actualizado exitosamente en {table_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error actualizando item en {table_name}: {e}")
            return False
    
    def delete_item(self, table_name, key):
        """Eliminar un item"""
        try:
            table = self.dynamodb_resource.Table(self.tables[table_name])
            table.delete_item(Key=key)
            logger.info(f"Item eliminado exitosamente de {table_name}")
            return True
            
        except ClientError as e:
            logger.error(f"Error eliminando item de {table_name}: {e}")
            return False
