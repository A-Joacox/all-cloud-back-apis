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
# Buscar .env en el directorio padre (ingesta/)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Si no encuentra en el padre, buscar en el directorio actual
if not os.path.exists(env_path):
    load_dotenv()

# Debug: Mostrar si las credenciales se están cargando
print(f"🔍 Debug - Archivo .env usado: {env_path}")
print(f"🔍 Debug - AWS_ACCESS_KEY_ID encontrado: {'Sí' if os.getenv('AWS_ACCESS_KEY_ID') else 'No'}")
print(f"🔍 Debug - AWS_SECRET_ACCESS_KEY encontrado: {'Sí' if os.getenv('AWS_SECRET_ACCESS_KEY') else 'No'}")
print(f"🔍 Debug - AWS_SESSION_TOKEN encontrado: {'Sí' if os.getenv('AWS_SESSION_TOKEN') else 'No'}")

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
            # Verificar cliente S3
            if not self.s3_client:
                logger.error("❌ Cliente S3 no inicializado")
                return False
                
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

    def extract_and_upload_all_tables(self):
        """Extraer y subir todas las tablas del sistema de salas"""
        connection = self.connect_to_mysql()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Tablas principales del sistema de salas
        tables = ['rooms', 'seats', 'schedules']
        
        try:
            # Verificar cliente S3
            if not self.s3_client:
                logger.error("❌ Cliente S3 no inicializado")
                return False
                
            # Crear bucket si no existe
            self.create_s3_bucket_if_not_exists()
            
            uploaded_files = []
            
            for table in tables:
                logger.info(f"🔄 Procesando tabla: {table}")
                
                # Extraer datos de la tabla completa
                query = f"SELECT * FROM {table}"
                df = pd.read_sql(query, connection)
                
                if not df.empty:
                    logger.info(f"📊 Datos extraídos de {table}: {len(df)} registros")
                    
                    # Subir como CSV
                    s3_key_csv = f"mysql-data/rooms/{table}_{timestamp}.csv"
                    csv_buffer = df.to_csv(index=False)
                    
                    self.s3_client.put_object(
                        Bucket=self.s3_bucket,
                        Key=s3_key_csv,
                        Body=csv_buffer,
                        ContentType='text/csv'
                    )
                    uploaded_files.append(s3_key_csv)
                    
                    # Subir como JSON
                    s3_key_json = f"mysql-data/rooms/{table}_{timestamp}.json"
                    json_buffer = df.to_json(orient='records', indent=2, date_format='iso')
                    
                    self.s3_client.put_object(
                        Bucket=self.s3_bucket,
                        Key=s3_key_json,
                        Body=json_buffer,
                        ContentType='application/json'
                    )
                    uploaded_files.append(s3_key_json)
                    
                    logger.info(f"✅ {table} subida exitosamente")
                    print(f"\n📋 Muestra de datos de {table}:")
                    print(df.head())
                else:
                    logger.warning(f"⚠️ No hay datos en la tabla {table}")
            
            # Crear archivo de metadatos
            metadata = {
                "extraction_date": datetime.now().isoformat(),
                "database_type": "mysql",
                "database_name": self.mysql_config['database'],
                "tables_exported": tables,
                "files_uploaded": uploaded_files,
                "total_files": len(uploaded_files),
                "host": self.mysql_config['host'],
                "port": self.mysql_config['port']
            }
            
            metadata_key = f"mysql-data/rooms/metadata_{timestamp}.json"
            metadata_buffer = json.dumps(metadata, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=metadata_key,
                Body=metadata_buffer,
                ContentType='application/json'
            )
            uploaded_files.append(metadata_key)
            
            logger.info(f"📁 Archivos subidos a S3: {len(uploaded_files)}")
            for file in uploaded_files:
                logger.info(f"   📄 s3://{self.s3_bucket}/{file}")
            
            return True
                
        finally:
            connection.close()

def main():
    """Función principal"""
    try:
        # Detectar si se ejecuta desde run-all-ingesta (modo automático)
        import sys
        auto_mode = len(sys.argv) > 1 and sys.argv[1] == 'auto'
        
        if auto_mode:
            print("🚀 Iniciando ingesta completa con AWS Academy...")
            ingestion = MySQLToS3Academy()
            result = ingestion.extract_and_upload_all_tables()
        else:
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