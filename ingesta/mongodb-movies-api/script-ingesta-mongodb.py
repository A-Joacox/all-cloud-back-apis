from pymongo import MongoClient
import pandas as pd
import boto3
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from bson import ObjectId

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class MongoDBToS3Academy:
    def __init__(self):
        # Configuración MongoDB
        self.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/cinema_movies')
        self.mongodb_database = os.getenv('MONGODB_DATABASE', 'cinema_movies')
        
        # Configuración AWS Academy (con Session Token)
        self.s3_bucket = os.getenv('S3_BUCKET', 'cinema-analytics-data')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Credenciales AWS Academy
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        
        if not all([aws_access_key, aws_secret_key, aws_session_token]):
            logger.error("❌ Faltan credenciales AWS Academy")
            logger.error("Necesitas: ACCESS_KEY, SECRET_KEY y SESSION_TOKEN")
            raise ValueError("Credenciales incompletas")
        
        # Cliente S3 con Session Token
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                aws_session_token=aws_session_token
            )
            
            # Probar credenciales
            self.s3_client.list_buckets()
            logger.info("✅ Credenciales AWS Academy válidas")
            
        except Exception as e:
            logger.error(f"❌ Error con credenciales AWS Academy: {e}")
            raise

    def create_s3_bucket_if_not_exists(self):
        """Crear bucket S3 si no existe"""
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"✅ Bucket {self.s3_bucket} ya existe")
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                try:
                    # Crear bucket
                    if self.aws_region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.s3_bucket)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.s3_bucket,
                            CreateBucketConfiguration={'LocationConstraint': self.aws_region}
                        )
                    logger.info(f"✅ Bucket {self.s3_bucket} creado exitosamente")
                except ClientError as create_error:
                    logger.error(f"❌ Error creando bucket: {create_error}")
                    raise
            else:
                logger.error(f"❌ Error accediendo al bucket: {e}")
                raise

    def connect_to_mongodb(self):
        """Conectar a MongoDB"""
        try:
            client = MongoClient(self.mongodb_uri)
            # Test the connection
            client.admin.command('ping')
            db = client[self.mongodb_database]
            logger.info("✅ Conexión exitosa a MongoDB")
            return client, db
        except Exception as err:
            logger.error(f"❌ Error conectando a MongoDB: {err}")
            raise

    def json_serial(self, obj):
        """JSON serializer para ObjectId y datetime"""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def extract_collection_data(self, db, collection_name, limit=None):
        """Extraer datos de una colección específica"""
        try:
            collection = db[collection_name]
            
            # Contar documentos
            total_docs = collection.count_documents({})
            logger.info(f"📊 Total de documentos en {collection_name}: {total_docs}")
            
            if total_docs == 0:
                return None
            
            # Extraer documentos
            query = {}
            cursor = collection.find(query)
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = list(cursor)
            logger.info(f"📊 Datos extraídos de {collection_name}: {len(documents)} documentos")
            
            # Convertir a DataFrame para procesamiento
            if documents:
                # Crear copia de documentos para DataFrame (no modificar originales)
                documents_for_df = []
                for doc in documents:
                    doc_copy = {}
                    for key, value in doc.items():
                        if isinstance(value, ObjectId):
                            doc_copy[key] = str(value)
                        elif isinstance(value, datetime):
                            doc_copy[key] = value.isoformat()
                        else:
                            doc_copy[key] = value
                    documents_for_df.append(doc_copy)
                
                df = pd.DataFrame(documents_for_df)
                return df, documents  # documents originales para JSON
            else:
                return None, None
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de {collection_name}: {e}")
            return None, None

    def upload_data_to_s3(self, df, raw_documents, s3_key_prefix, format_type='csv'):
        """Subir datos a S3 en diferentes formatos"""
        uploaded_files = []
        
        try:
            if format_type in ['csv', 'both'] and df is not None:
                # Subir como CSV
                s3_key = f"{s3_key_prefix}.csv"
                csv_buffer = df.to_csv(index=False)
                
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=csv_buffer,
                    ContentType='text/csv'
                )
                
                uploaded_files.append(s3_key)
                logger.info(f"✅ CSV subido: s3://{self.s3_bucket}/{s3_key}")
            
            if format_type in ['json', 'both'] and raw_documents is not None:
                # Subir como JSON (mantiene estructura MongoDB)
                s3_key = f"{s3_key_prefix}.json"
                json_buffer = json.dumps(raw_documents, indent=2, default=self.json_serial)
                
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=json_buffer,
                    ContentType='application/json'
                )
                
                uploaded_files.append(s3_key)
                logger.info(f"✅ JSON subido: s3://{self.s3_bucket}/{s3_key}")
            
            return uploaded_files
        except Exception as e:
            logger.error(f"❌ Error subiendo archivos: {e}")
            return []

    def extract_and_upload_all_collections(self):
        """Extraer y subir todas las colecciones del sistema de películas"""
        client, db = self.connect_to_mongodb()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Colecciones principales del sistema de películas
        collections = ['movies', 'genres']
        
        try:
            # Crear bucket si no existe
            self.create_s3_bucket_if_not_exists()
            
            uploaded_files = []
            
            for collection_name in collections:
                logger.info(f"🔄 Procesando colección: {collection_name}")
                
                # Extraer datos
                df, raw_documents = self.extract_collection_data(db, collection_name)
                
                if df is not None and not df.empty:
                    # Subir en ambos formatos
                    s3_key_prefix = f"mongodb-data/movies/{collection_name}_{timestamp}"
                    
                    # Subir CSV
                    files_csv = self.upload_data_to_s3(df, raw_documents, s3_key_prefix, 'csv')
                    uploaded_files.extend(files_csv)
                    
                    # Subir JSON
                    files_json = self.upload_data_to_s3(df, raw_documents, s3_key_prefix, 'json')
                    uploaded_files.extend(files_json)
                    
                    # Mostrar muestra de datos
                    print(f"\n📋 Muestra de datos de {collection_name}:")
                    print(df.head())
                else:
                    logger.warning(f"⚠️ No hay datos en la colección {collection_name}")
            
            # Crear un archivo de metadatos
            metadata = {
                "extraction_date": datetime.now().isoformat(),
                "database_type": "mongodb",
                "database_name": self.mongodb_database,
                "collections_exported": collections,
                "files_uploaded": uploaded_files,
                "total_files": len(uploaded_files),
                "mongodb_uri": self.mongodb_uri.replace(self.mongodb_uri.split('@')[0].split('//')[1], '***') if '@' in self.mongodb_uri else self.mongodb_uri
            }
            
            metadata_key = f"mongodb-data/movies/metadata_{timestamp}.json"
            metadata_buffer = json.dumps(metadata, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=metadata_key,
                Body=metadata_buffer,
                ContentType='application/json'
            )
            
            logger.info(f"✅ Metadata creado: s3://{self.s3_bucket}/{metadata_key}")
            
            # Verificar archivos subidos
            objects = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix="mongodb-data/movies/"
            )
            
            if 'Contents' in objects:
                logger.info(f"📂 Total de archivos en S3: {len(objects['Contents'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la extracción: {e}")
            return False
        finally:
            client.close()

    def extract_and_upload_test(self):
        """Test de extracción y subida con una colección pequeña"""
        client, db = self.connect_to_mongodb()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Crear bucket si no existe
            self.create_s3_bucket_if_not_exists()
            
            # Test con colección de géneros (más pequeña)
            df, raw_documents = self.extract_collection_data(db, 'genres', limit=3)
            
            if df is not None and not df.empty:
                logger.info(f"📊 Datos extraídos: {len(df)} documentos")
                print(df.head())
                
                # Subir a S3
                s3_key_prefix = f"mongodb-data/test/genres_test_{timestamp}"
                uploaded_files = self.upload_data_to_s3(df, raw_documents, s3_key_prefix, 'both')
                
                if uploaded_files:
                    logger.info(f"✅ Test exitoso! Archivos: {uploaded_files}")
                    return True
            else:
                logger.warning("⚠️ No hay datos en la colección genres")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en test: {e}")
            return False
        finally:
            client.close()

def main():
    """Función principal"""
    try:
        print("🚀 Iniciando ingesta MongoDB con AWS Academy...")
        
        ingestion = MongoDBToS3Academy()
        
        # Detectar si se ejecuta desde run-all-ingesta (modo automático)
        import sys
        auto_mode = len(sys.argv) > 1 and sys.argv[1] == 'auto'
        
        if auto_mode:
            # Modo automático: ejecutar extracción completa
            print("\n📦 Modo automático: Ejecutando extracción completa...")
            result = ingestion.extract_and_upload_all_collections()
        else:
            # Modo interactivo
            choice = input("\n¿Qué deseas hacer?\n1. Test rápido\n2. Extracción completa\nElige (1/2): ").strip()
            
            if choice == '1':
                print("\n🧪 Ejecutando test...")
                result = ingestion.extract_and_upload_test()
            elif choice == '2':
                print("\n📦 Ejecutando extracción completa...")
                result = ingestion.extract_and_upload_all_collections()
            else:
                print("❌ Opción no válida")
                return
        
        if result:
            print("\n✅ ¡Ingesta completada exitosamente!")
            print("🎉 Los datos de MongoDB han sido subidos a S3")
        else:
            print("\n❌ La ingesta falló")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print("\n🔧 Para solucionar:")
        print("1. Verifica la conexión a MongoDB")
        print("2. Copia las 3 líneas de AWS Academy CLI")
        print("3. Pégalas en terminal (export...)")
        print("4. O actualiza el archivo .env con SESSION_TOKEN")

if __name__ == "__main__":
    main()