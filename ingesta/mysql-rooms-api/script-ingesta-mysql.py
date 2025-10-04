import mysql.connector
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

class MySQLToS3Academy:
    def __init__(self):
        # Configuración MySQL
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3307)),
            'user': os.getenv('MYSQL_USER', 'cinema_user'),
            'password': os.getenv('MYSQL_PASSWORD', 'cinema_password'),
            'database': os.getenv('MYSQL_DATABASE', 'cinema_rooms')
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

    def connect_to_mysql(self):
        """Conectar a MySQL"""
        try:
            connection = mysql.connector.connect(**self.mysql_config)
            logger.info("✅ Conexión exitosa a MySQL")
            return connection
        except mysql.connector.Error as err:
            logger.error(f"❌ Error conectando a MySQL: {err}")
            raise

    def extract_and_upload_test(self):
        """Test de extracción y subida"""
        connection = self.connect_to_mysql()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Crear bucket si no existe
            self.create_s3_bucket_if_not_exists()
            
            # Consulta de prueba
            query = "SELECT * FROM rooms LIMIT 3"
            df = pd.read_sql(query, connection)
            
            if not df.empty:
                logger.info(f"📊 Datos extraídos: {len(df)} registros")
                print(df.head())
                
                # Subir a S3
                s3_key = f"mysql-data/test/rooms_test_{timestamp}.csv"
                csv_buffer = df.to_csv(index=False)
                
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=s3_key,
                    Body=csv_buffer,
                    ContentType='text/csv'
                )
                
                logger.info(f"✅ Test exitoso!")
                logger.info(f"📁 Archivo: s3://{self.s3_bucket}/{s3_key}")
                
                # Verificar que se subió
                objects = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix="mysql-data/test/"
                )
                
                if 'Contents' in objects:
                    logger.info(f"📂 Archivos en S3: {len(objects['Contents'])}")
                
                return True
            else:
                logger.warning("⚠️ No hay datos en la tabla rooms")
                return False
                
        finally:
            connection.close()

def main():
    """Función principal"""
    try:
        print("🚀 Iniciando test con AWS Academy...")
        
        ingestion = MySQLToS3Academy()
        result = ingestion.extract_and_upload_test()
        
        if result:
            print("\n✅ ¡Test exitoso con AWS Academy!")
            print("🎉 Listo para ingesta completa")
        else:
            print("\n❌ Test falló")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        print("\n🔧 Para solucionar:")
        print("1. Copia las 3 líneas de AWS Academy CLI")
        print("2. Pégalas en terminal (export...)")
        print("3. O actualiza el archivo .env con SESSION_TOKEN")

if __name__ == "__main__":
    main()