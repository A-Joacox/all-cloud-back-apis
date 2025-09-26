import mysql.connector
import random
import string
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'cinema_rooms')
}

# Datos de ejemplo
SCREEN_TYPES = ['2D', '3D', 'IMAX']
SEAT_TYPES = ['regular', 'premium', 'vip']
ROOM_NAMES = [
    'Sala Principal', 'Sala VIP', 'Sala 3D', 'Sala IMAX', 'Sala Premium',
    'Sala 1', 'Sala 2', 'Sala 3', 'Sala 4', 'Sala 5',
    'Sala A', 'Sala B', 'Sala C', 'Sala D', 'Sala E',
    'Sala Norte', 'Sala Sur', 'Sala Este', 'Sala Oeste', 'Sala Central'
]

def generate_room():
    """Genera una sala"""
    return {
        'name': random.choice(ROOM_NAMES) + f" {random.randint(1, 50)}",
        'capacity': random.randint(50, 200),
        'screen_type': random.choice(SCREEN_TYPES),
        'is_active': random.choice([True, True, True, False])  # 75% activas
    }

def generate_seats(room_id, capacity):
    """Genera asientos para una sala"""
    seats = []
    rows = capacity // 10  # Asumiendo 10 asientos por fila
    if rows == 0:
        rows = 1
    
    seat_count = 0
    for row in range(rows):
        seats_in_row = min(10, capacity - seat_count)
        for seat_num in range(1, seats_in_row + 1):
            seat_type = 'vip' if seat_num <= 2 else ('premium' if seat_num <= 6 else 'regular')
            seats.append({
                'room_id': room_id,
                'row_number': chr(65 + row),  # A, B, C, etc.
                'seat_number': seat_num,
                'seat_type': seat_type,
                'is_available': random.choice([True, True, True, False])  # 75% disponibles
            })
            seat_count += 1
            if seat_count >= capacity:
                break
        if seat_count >= capacity:
            break
    
    return seats

def generate_schedule():
    """Genera un horario"""
    # Generar fecha aleatoria en los últimos 2 años
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now() + timedelta(days=30)
    
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days),
        hours=random.randint(9, 23),
        minutes=random.choice([0, 15, 30, 45])
    )
    
    return {
        'movie_id': f"507f1f77bcf86cd799{random.randint(100000, 999999)}",
        'room_id': random.randint(1, 100),  # Asumiendo 100 salas
        'show_time': random_date,
        'price': round(random.uniform(5.0, 25.0), 2),
        'is_active': random.choice([True, True, True, False])  # 75% activos
    }

def generate_data():
    """Función principal para generar datos"""
    connection = None
    
    try:
        # Conectar a MySQL
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        
        print("Conectado a MySQL")
        
        # Generar salas
        print("Generando salas...")
        rooms = []
        ROOMS_COUNT = 100  # 100 salas
        
        for i in range(ROOMS_COUNT):
            rooms.append(generate_room())
        
        # Insertar salas
        insert_room_query = """
        INSERT INTO rooms (name, capacity, screen_type, is_active, created_at, updated_at)
        VALUES (%(name)s, %(capacity)s, %(screen_type)s, %(is_active)s, NOW(), NOW())
        """
        
        cursor.executemany(insert_room_query, rooms)
        connection.commit()
        print(f"✅ Insertadas {len(rooms)} salas")
        
        # Generar asientos para cada sala
        print("Generando asientos...")
        all_seats = []
        
        for room_id in range(1, ROOMS_COUNT + 1):
            room = rooms[room_id - 1]
            seats = generate_seats(room_id, room['capacity'])
            all_seats.extend(seats)
            
            # Insertar en lotes de 1000
            if len(all_seats) >= 1000:
                insert_seat_query = """
                INSERT INTO seats (room_id, row_number, seat_number, seat_type, is_available, created_at)
                VALUES (%(room_id)s, %(row_number)s, %(seat_number)s, %(seat_type)s, %(is_available)s, NOW())
                """
                cursor.executemany(insert_seat_query, all_seats)
                connection.commit()
                print(f"✅ Insertados {len(all_seats)} asientos (lote)")
                all_seats = []
        
        # Insertar asientos restantes
        if all_seats:
            insert_seat_query = """
            INSERT INTO seats (room_id, row_number, seat_number, seat_type, is_available, created_at)
            VALUES (%(room_id)s, %(row_number)s, %(seat_number)s, %(seat_type)s, %(is_available)s, NOW())
            """
            cursor.executemany(insert_seat_query, all_seats)
            connection.commit()
            print(f"✅ Insertados {len(all_seats)} asientos restantes")
        
        # Generar horarios
        print("Generando horarios...")
        schedules = []
        SCHEDULES_COUNT = 12000  # 12,000 horarios
        
        for i in range(SCHEDULES_COUNT):
            schedules.append(generate_schedule())
            
            # Insertar en lotes de 1000
            if len(schedules) >= 1000:
                insert_schedule_query = """
                INSERT INTO schedules (movie_id, room_id, show_time, price, is_active, created_at)
                VALUES (%(movie_id)s, %(room_id)s, %(show_time)s, %(price)s, %(is_active)s, NOW())
                """
                cursor.executemany(insert_schedule_query, schedules)
                connection.commit()
                print(f"✅ Insertados {len(schedules)} horarios (lote)")
                schedules = []
        
        # Insertar horarios restantes
        if schedules:
            insert_schedule_query = """
            INSERT INTO schedules (movie_id, room_id, show_time, price, is_active, created_at)
            VALUES (%(movie_id)s, %(room_id)s, %(show_time)s, %(price)s, %(is_active)s, NOW())
            """
            cursor.executemany(insert_schedule_query, schedules)
            connection.commit()
            print(f"✅ Insertados {len(schedules)} horarios restantes")
        
        print(f"🏢 Total de salas generadas: {ROOMS_COUNT}")
        print(f"💺 Total de asientos generados: {sum(room['capacity'] for room in rooms)}")
        print(f"🎬 Total de horarios generados: {SCHEDULES_COUNT}")
        
    except mysql.connector.Error as error:
        print(f"Error de MySQL: {error}")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    generate_data()