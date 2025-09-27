#!/usr/bin/env python3
"""
Script para configurar recursos de AWS necesarios para el servicio de ingesta
"""

import boto3
import logging
from botocore.exceptions import ClientError
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_s3_bucket():
    """Crear bucket de S3 si no existe"""
    try:
        s3_client = boto3.client('s3')
        bucket_name = Config.S3_BUCKET_NAME
        
        # Verificar si el bucket existe
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} ya existe")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket no existe, crearlo
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    logger.info(f"Bucket {bucket_name} creado exitosamente")
                    
                    # Configurar versionado
                    s3_client.put_bucket_versioning(
                        Bucket=bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                    
                    # Configurar encriptación
                    s3_client.put_bucket_encryption(
                        Bucket=bucket_name,
                        ServerSideEncryptionConfiguration={
                            'Rules': [
                                {
                                    'ApplyServerSideEncryptionByDefault': {
                                        'SSEAlgorithm': 'AES256'
                                    }
                                }
                            ]
                        }
                    )
                    
                    return True
                except ClientError as create_error:
                    logger.error(f"Error creando bucket: {create_error}")
                    return False
            else:
                logger.error(f"Error verificando bucket: {e}")
                return False
                
    except Exception as e:
        logger.error(f"Error general con S3: {e}")
        return False

def create_dynamodb_tables():
    """Crear tablas de DynamoDB"""
    try:
        dynamodb = boto3.resource('dynamodb')
        
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
        
        created_tables = []
        
        for table_name, config in tables_config.items():
            full_table_name = Config.DYNAMODB_TABLES[table_name]
            
            try:
                # Verificar si la tabla existe
                table = dynamodb.Table(full_table_name)
                table.load()
                logger.info(f"Tabla {full_table_name} ya existe")
                created_tables.append(full_table_name)
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceNotFoundException':
                    # Crear tabla
                    try:
                        create_params = {
                            'TableName': full_table_name,
                            'KeySchema': config['key_schema'],
                            'AttributeDefinitions': config['attribute_definitions'],
                            'BillingMode': 'PAY_PER_REQUEST'
                        }
                        
                        if config.get('global_secondary_indexes'):
                            create_params['GlobalSecondaryIndexes'] = config['global_secondary_indexes']
                        
                        table = dynamodb.create_table(**create_params)
                        logger.info(f"Tabla {full_table_name} creada exitosamente")
                        created_tables.append(full_table_name)
                        
                        # Esperar a que la tabla esté activa
                        table.wait_until_exists()
                        
                    except ClientError as create_error:
                        logger.error(f"Error creando tabla {full_table_name}: {create_error}")
                else:
                    logger.error(f"Error verificando tabla {full_table_name}: {e}")
        
        return created_tables
        
    except Exception as e:
        logger.error(f"Error general con DynamoDB: {e}")
        return []

def create_iam_role():
    """Crear rol de IAM para el servicio"""
    try:
        iam_client = boto3.client('iam')
        role_name = 'CinemaDataIngestionRole'
        
        # Política de confianza
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Política de permisos
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{Config.S3_BUCKET_NAME}",
                        f"arn:aws:s3:::{Config.S3_BUCKET_NAME}/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:Query",
                        "dynamodb:Scan",
                        "dynamodb:BatchGetItem",
                        "dynamodb:BatchWriteItem"
                    ],
                    "Resource": "*"
                }
            ]
        }
        
        try:
            # Verificar si el rol existe
            iam_client.get_role(RoleName=role_name)
            logger.info(f"Rol {role_name} ya existe")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchEntity':
                # Crear rol
                try:
                    iam_client.create_role(
                        RoleName=role_name,
                        AssumeRolePolicyDocument=str(trust_policy).replace("'", '"')
                    )
                    
                    # Adjuntar política
                    iam_client.put_role_policy(
                        RoleName=role_name,
                        PolicyName='CinemaDataIngestionPolicy',
                        PolicyDocument=str(policy_document).replace("'", '"')
                    )
                    
                    logger.info(f"Rol {role_name} creado exitosamente")
                    return True
                    
                except ClientError as create_error:
                    logger.error(f"Error creando rol: {create_error}")
                    return False
            else:
                logger.error(f"Error verificando rol: {e}")
                return False
                
    except Exception as e:
        logger.error(f"Error general con IAM: {e}")
        return False

def main():
    """Función principal"""
    logger.info("Iniciando configuración de recursos AWS")
    
    results = {
        's3_bucket': create_s3_bucket(),
        'dynamodb_tables': create_dynamodb_tables(),
        'iam_role': create_iam_role()
    }
    
    logger.info("Configuración completada:")
    logger.info(f"S3 Bucket: {'✅' if results['s3_bucket'] else '❌'}")
    logger.info(f"DynamoDB Tables: {len(results['dynamodb_tables'])} creadas")
    logger.info(f"IAM Role: {'✅' if results['iam_role'] else '❌'}")

if __name__ == '__main__':
    main()
