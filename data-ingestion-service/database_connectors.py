import logging
import json
from datetime import datetime
import mysql.connector
import psycopg2
from pymongo import MongoClient
from sqlalchemy import create_engine, text
from config import Config

logger = logging.getLogger(__name__)

class MySQLConnector:
    """Conector para MySQL (Rooms API)"""
    
    def __init__(self):
        self.config = Config.MYSQL_CONFIG
        self.connection = None
    
    def connect(self):
        """Establecer conexión a MySQL"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            logger.info("Conexión a MySQL establecida exitosamente")
            return True
        except mysql.connector.Error as e:
            logger.error(f"Error conectando a MySQL: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Conexión a MySQL cerrada")
    
    def fetch_rooms(self):
        """Obtener todas las salas"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()
            cursor.close()
            
            # Convertir datetime objects a strings para JSON
            for room in rooms:
                if room.get('created_at'):
                    room['created_at'] = room['created_at'].isoformat()
                if room.get('updated_at'):
                    room['updated_at'] = room['updated_at'].isoformat()
            
            logger.info(f"Obtenidas {len(rooms)} salas de MySQL")
            return rooms
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo salas: {e}")
            return []
    
    def fetch_seats(self):
        """Obtener todos los asientos"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM seats")
            seats = cursor.fetchall()
            cursor.close()
            
            # Convertir datetime objects a strings
            for seat in seats:
                if seat.get('created_at'):
                    seat['created_at'] = seat['created_at'].isoformat()
            
            logger.info(f"Obtenidos {len(seats)} asientos de MySQL")
            return seats
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo asientos: {e}")
            return []
    
    def fetch_schedules(self):
        """Obtener todos los horarios"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM schedules")
            schedules = cursor.fetchall()
            cursor.close()
            
            # Convertir datetime objects a strings
            for schedule in schedules:
                if schedule.get('show_time'):
                    schedule['show_time'] = schedule['show_time'].isoformat()
                if schedule.get('created_at'):
                    schedule['created_at'] = schedule['created_at'].isoformat()
            
            logger.info(f"Obtenidos {len(schedules)} horarios de MySQL")
            return schedules
        except mysql.connector.Error as e:
            logger.error(f"Error obteniendo horarios: {e}")
            return []

class PostgreSQLConnector:
    """Conector para PostgreSQL (Reservations API)"""
    
    def __init__(self):
        self.config = Config.POSTGRESQL_CONFIG
        self.connection = None
    
    def connect(self):
        """Establecer conexión a PostgreSQL"""
        try:
            self.connection = psycopg2.connect(**self.config)
            logger.info("Conexión a PostgreSQL establecida exitosamente")
            return True
        except psycopg2.Error as e:
            logger.error(f"Error conectando a PostgreSQL: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión"""
        if self.connection:
            self.connection.close()
            logger.info("Conexión a PostgreSQL cerrada")
    
    def fetch_users(self):
        """Obtener todos los usuarios"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users")
            
            columns = [desc[0] for desc in cursor.description]
            users = []
            
            for row in cursor.fetchall():
                user = dict(zip(columns, row))
                # Convertir datetime objects a strings
                if user.get('created_at'):
                    user['created_at'] = user['created_at'].isoformat()
                if user.get('updated_at'):
                    user['updated_at'] = user['updated_at'].isoformat()
                users.append(user)
            
            cursor.close()
            logger.info(f"Obtenidos {len(users)} usuarios de PostgreSQL")
            return users
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            return []
    
    def fetch_reservations(self):
        """Obtener todas las reservas"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM reservations")
            
            columns = [desc[0] for desc in cursor.description]
            reservations = []
            
            for row in cursor.fetchall():
                reservation = dict(zip(columns, row))
                # Convertir datetime objects a strings
                if reservation.get('reservation_date'):
                    reservation['reservation_date'] = reservation['reservation_date'].isoformat()
                if reservation.get('created_at'):
                    reservation['created_at'] = reservation['created_at'].isoformat()
                if reservation.get('updated_at'):
                    reservation['updated_at'] = reservation['updated_at'].isoformat()
                reservations.append(reservation)
            
            cursor.close()
            logger.info(f"Obtenidas {len(reservations)} reservas de PostgreSQL")
            return reservations
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo reservas: {e}")
            return []
    
    def fetch_reserved_seats(self):
        """Obtener todos los asientos reservados"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM reserved_seats")
            
            columns = [desc[0] for desc in cursor.description]
            reserved_seats = []
            
            for row in cursor.fetchall():
                reserved_seat = dict(zip(columns, row))
                if reserved_seat.get('created_at'):
                    reserved_seat['created_at'] = reserved_seat['created_at'].isoformat()
                reserved_seats.append(reserved_seat)
            
            cursor.close()
            logger.info(f"Obtenidos {len(reserved_seats)} asientos reservados de PostgreSQL")
            return reserved_seats
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo asientos reservados: {e}")
            return []
    
    def fetch_payments(self):
        """Obtener todos los pagos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM payments")
            
            columns = [desc[0] for desc in cursor.description]
            payments = []
            
            for row in cursor.fetchall():
                payment = dict(zip(columns, row))
                if payment.get('payment_date'):
                    payment['payment_date'] = payment['payment_date'].isoformat()
                if payment.get('created_at'):
                    payment['created_at'] = payment['created_at'].isoformat()
                payments.append(payment)
            
            cursor.close()
            logger.info(f"Obtenidos {len(payments)} pagos de PostgreSQL")
            return payments
        except psycopg2.Error as e:
            logger.error(f"Error obteniendo pagos: {e}")
            return []

class MongoDBConnector:
    """Conector para MongoDB (Movies API)"""
    
    def __init__(self):
        self.uri = Config.MONGODB_URI
        self.client = None
        self.db = None
    
    def connect(self):
        """Establecer conexión a MongoDB"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client.get_default_database()
            logger.info("Conexión a MongoDB establecida exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error conectando a MongoDB: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión"""
        if self.client:
            self.client.close()
            logger.info("Conexión a MongoDB cerrada")
    
    def fetch_movies(self):
        """Obtener todas las películas"""
        try:
            movies_collection = self.db.movies
            movies = list(movies_collection.find())
            
            # Convertir ObjectId a string para JSON serialization
            for movie in movies:
                if '_id' in movie:
                    movie['_id'] = str(movie['_id'])
            
            logger.info(f"Obtenidas {len(movies)} películas de MongoDB")
            return movies
        except Exception as e:
            logger.error(f"Error obteniendo películas: {e}")
            return []
    
    def fetch_genres(self):
        """Obtener todos los géneros"""
        try:
            genres_collection = self.db.genres
            genres = list(genres_collection.find())
            
            # Convertir ObjectId a string
            for genre in genres:
                if '_id' in genre:
                    genre['_id'] = str(genre['_id'])
            
            logger.info(f"Obtenidos {len(genres)} géneros de MongoDB")
            return genres
        except Exception as e:
            logger.error(f"Error obteniendo géneros: {e}")
            return []

class DatabaseManager:
    """Manager para todos los conectores de base de datos"""
    
    def __init__(self):
        self.mysql_connector = MySQLConnector()
        self.postgresql_connector = PostgreSQLConnector()
        self.mongodb_connector = MongoDBConnector()
    
    def connect_all(self):
        """Conectar a todas las bases de datos"""
        results = {}
        
        results['mysql'] = self.mysql_connector.connect()
        results['postgresql'] = self.postgresql_connector.connect()
        results['mongodb'] = self.mongodb_connector.connect()
        
        return results
    
    def disconnect_all(self):
        """Desconectar de todas las bases de datos"""
        self.mysql_connector.disconnect()
        self.postgresql_connector.disconnect()
        self.mongodb_connector.disconnect()
    
    def fetch_all_data(self):
        """Obtener todos los datos de todas las bases de datos"""
        data = {
            'mysql': {
                'rooms': self.mysql_connector.fetch_rooms(),
                'seats': self.mysql_connector.fetch_seats(),
                'schedules': self.mysql_connector.fetch_schedules()
            },
            'postgresql': {
                'users': self.postgresql_connector.fetch_users(),
                'reservations': self.postgresql_connector.fetch_reservations(),
                'reserved_seats': self.postgresql_connector.fetch_reserved_seats(),
                'payments': self.postgresql_connector.fetch_payments()
            },
            'mongodb': {
                'movies': self.mongodb_connector.fetch_movies(),
                'genres': self.mongodb_connector.fetch_genres()
            }
        }
        
        return data
