import psycopg2
import pandas as pd
import boto3
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError, NoCredentialsError

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class PostgreSQLToS3Academy:
    def __init__(self):
        # Configuración PostgreSQL
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'cinema_password'),
            'database': os.getenv('POSTGRES_DATABASE', 'cinema_reservations')
        }
        
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

    def connect_to_postgresql(self):
        """Conectar a PostgreSQL"""
        try:
            connection = psycopg2.connect(**self.postgres_config)
            logger.info("✅ Conexión exitosa a PostgreSQL")
            return connection
        except psycopg2.Error as err:
            logger.error(f"❌ Error conectando a PostgreSQL: {err}")
            raise

    def extract_table_data(self, connection, table_name, limit=None):
        """Extraer datos de una tabla específica"""
        try:
            query = f"SELECT * FROM {table_name}"
            if limit:
                query += f" LIMIT {limit}"
            
            df = pd.read_sql(query, connection)
            logger.info(f"📊 Datos extraídos de {table_name}: {len(df)} registros")
            return df
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de {table_name}: {e}")
            return None

    def upload_dataframe_to_s3(self, df, s3_key, format_type='csv'):
        """Subir DataFrame a S3"""
        try:
            if format_type == 'csv':
                buffer = df.to_csv(index=False)
                content_type = 'text/csv'
            elif format_type == 'json':
                # Convert datetime objects to string for JSON serialization
                df_json = df.copy()
                for col in df_json.columns:
                    if df_json[col].dtype == 'datetime64[ns]':
                        df_json[col] = df_json[col].dt.isoformat()
                buffer = df_json.to_json(orient='records', indent=2)
                content_type = 'application/json'
            else:
                raise ValueError(f"Formato no soportado: {format_type}")
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=buffer,
                ContentType=content_type
            )
            
            logger.info(f"✅ Archivo subido: s3://{self.s3_bucket}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"❌ Error subiendo archivo: {e}")
            return False

    def extract_and_upload_all_tables(self):
        """Extraer y subir todas las tablas del sistema de reservas"""
        connection = self.connect_to_postgresql()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Tablas principales del sistema de reservas
        tables = ['users', 'reservations', 'reserved_seats', 'payments']
        
        try:
            # Crear bucket si no existe
            self.create_s3_bucket_if_not_exists()
            
            uploaded_files = []
            
            for table in tables:
                logger.info(f"🔄 Procesando tabla: {table}")
                
                # Extraer datos
                df = self.extract_table_data(connection, table)
                
                if df is not None and not df.empty:
                    # Subir como CSV
                    s3_key_csv = f"postgresql-data/reservations/{table}_{timestamp}.csv"
                    if self.upload_dataframe_to_s3(df, s3_key_csv, 'csv'):
                        uploaded_files.append(s3_key_csv)
                    
                    # Subir como JSON
                    s3_key_json = f"postgresql-data/reservations/{table}_{timestamp}.json"
                    if self.upload_dataframe_to_s3(df, s3_key_json, 'json'):
                        uploaded_files.append(s3_key_json)
                    
                    # Mostrar muestra de datos
                    print(f"\n📋 Muestra de datos de {table}:")
                    print(df.head())
                else:
                    logger.warning(f"⚠️ No hay datos en la tabla {table}")
            
            # Crear un archivo de metadatos
            metadata = {
                "extraction_date": datetime.now().isoformat(),
                "database_type": "postgresql",
                "database_name": self.postgres_config['database'],
                "tables_exported": tables,
                "files_uploaded": uploaded_files,
                "total_files": len(uploaded_files)
            }
            
            metadata_key = f"postgresql-data/reservations/metadata_{timestamp}.json"
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
                Prefix="postgresql-data/reservations/"
            )
            
            if 'Contents' in objects:
                logger.info(f"📂 Total de archivos en S3: {len(objects['Contents'])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error durante la extracción: {e}")
            return False
        finally:
            connection.close()

    def extract_and_upload_test(self):
        """Test de extracción y subida con una tabla pequeña"""
        connection = self.connect_to_postgresql()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Crear bucket si no existe
            self.create_s3_bucket_if_not_exists()
            
            # Consulta de prueba (usuarios)
            df = self.extract_table_data(connection, 'users', limit=3)
            
            if df is not None and not df.empty:
                logger.info(f"📊 Datos extraídos: {len(df)} registros")
                print(df.head())
                
                # Subir a S3
                s3_key = f"postgresql-data/test/users_test_{timestamp}.csv"
                if self.upload_dataframe_to_s3(df, s3_key, 'csv'):
                    logger.info(f"✅ Test exitoso!")
                    return True
            else:
                logger.warning("⚠️ No hay datos en la tabla users")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error en test: {e}")
            return False
        finally:
            connection.close()

def main():
    """Función principal"""
    try:
        print("🚀 Iniciando ingesta PostgreSQL con AWS Academy...")
        
        ingestion = PostgreSQLToS3Academy()
        
        # Detectar si se ejecuta desde run-all-ingesta (modo automático)
        import sys
        auto_mode = len(sys.argv) > 1 and sys.argv[1] == 'auto'
        
        if auto_mode:
            # Modo automático: ejecutar extracción completa
            print("\n📦 Modo automático: Ejecutando extracción completa...")
            result = ingestion.extract_and_upload_all_tables()
        else:
            # Modo interactivo
            choice = input("\n¿Qué deseas hacer?\n1. Test rápido\n2. Extracción completa\nElige (1/2): ").strip()
            
            if choice == '1':
                print("\n🧪 Ejecutando test...")
                result = ingestion.extract_and_upload_test()
            elif choice == '2':
                print("\n📦 Ejecutando extracción completa...")
                result = ingestion.extract_and_upload_all_tables()
            else:
                print("❌ Opción no válida")
                return
        
        if result:
            print("\n✅ ¡Ingesta completada exitosamente!")
            print("🎉 Los datos de PostgreSQL han sido subidos a S3")
        else:
            print("\n❌ La ingesta falló")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print("\n🔧 Para solucionar:")
        print("1. Verifica la conexión a PostgreSQL")
        print("2. Copia las 3 líneas de AWS Academy CLI")
        print("3. Pégalas en terminal (export...)")
        print("4. O actualiza el archivo .env con SESSION_TOKEN")

if __name__ == "__main__":
    main()