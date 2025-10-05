import mysql.connector
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3307)),
    'user': os.getenv('MYSQL_USER', 'cinema_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'cinema_password'),
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

def create_tables_if_not_exist(cursor):
    """Crear tablas si no existen"""
    print("🔧 Verificando y creando tablas si es necesario...")
    
    # Tabla rooms
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            capacity INT NOT NULL,
            screen_type VARCHAR(50) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla seats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_id INT NOT NULL,
            row_number VARCHAR(10) NOT NULL,
            seat_number INT NOT NULL,
            seat_type VARCHAR(50) NOT NULL DEFAULT 'regular',
            is_available BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE,
            UNIQUE KEY unique_seat (room_id, row_number, seat_number)
        )
    """)
    
    # Tabla schedules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_id INT NOT NULL,
            movie_id VARCHAR(100) NOT NULL,
            show_time DATETIME NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
        )
    """)
    
    print("✅ Tablas verificadas/creadas correctamente")

def generate_room():
    return {
        'name': random.choice(ROOM_NAMES) + f" {random.randint(1, 50)}",
        'capacity': random.randint(50, 200),
        'screen_type': random.choice(SCREEN_TYPES),
        'is_active': random.choice([True, True, True, False])  # 75% activas
    }

def generate_seats(room_id, capacity):
    seats = []
    rows = capacity // 10
    if rows == 0:
        rows = 1
    
    seat_count = 0
    for row in range(rows):
        seats_in_row = min(10, capacity - seat_count)
        for seat_num in range(1, seats_in_row + 1):
            seat_type = 'vip' if seat_num <= 2 else ('premium' if seat_num <= 6 else 'regular')
            seats.append({
                'room_id': room_id,
                'row_number': chr(65 + row),
                'seat_number': seat_num,
                'seat_type': seat_type,
                'is_available': random.choice([True, True, True, False])
            })
            seat_count += 1
            if seat_count >= capacity:
                break
        if seat_count >= capacity:
            break
    return seats

def generate_schedule():
    start_date = datetime.now() - timedelta(days=730)
    end_date = datetime.now() + timedelta(days=30)
    
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days),
        hours=random.randint(9, 23),
        minutes=random.choice([0, 15, 30, 45])
    )
    
    return {
        'movie_id': f"507f1f77bcf86cd799{random.randint(100000, 999999)}",
        'room_id': random.randint(1, 100),
        'show_time': random_date,
        'price': round(random.uniform(5.0, 25.0), 2),
        'is_active': random.choice([True, True, True, False])
    }

def generate_data():
    connection = None
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = connection.cursor()
        print("Conectado a MySQL")
        
        # Crear tablas si no existen
        create_tables_if_not_exist(cursor)
        connection.commit()
        
        # Insertar salas
        print("Generando salas...")
        rooms = [generate_room() for _ in range(100)]
        insert_room_query = """
        INSERT INTO rooms (name, capacity, screen_type, is_active)
        VALUES (%(name)s, %(capacity)s, %(screen_type)s, %(is_active)s)
        """
        cursor.executemany(insert_room_query, rooms)
        connection.commit()
        print(f"✅ Insertadas {len(rooms)} salas")
        
        # Insertar asientos
        print("Generando asientos...")
        all_seats = []
        for room_id in range(1, 101):
            seats = generate_seats(room_id, rooms[room_id - 1]['capacity'])
            all_seats.extend(seats)
            if len(all_seats) >= 1000:
                insert_seat_query = """
                INSERT INTO seats (room_id, `row_number`, seat_number, seat_type, is_available)
                VALUES (%(room_id)s, %(row_number)s, %(seat_number)s, %(seat_type)s, %(is_available)s)
                """
                cursor.executemany(insert_seat_query, all_seats)
                connection.commit()
                print(f"✅ Insertados {len(all_seats)} asientos (lote)")
                all_seats = []
        if all_seats:
            insert_seat_query = """
            INSERT INTO seats (room_id, `row_number`, seat_number, seat_type, is_available)
            VALUES (%(room_id)s, %(row_number)s, %(seat_number)s, %(seat_type)s, %(is_available)s)
            """
            cursor.executemany(insert_seat_query, all_seats)
            connection.commit()
            print(f"✅ Insertados {len(all_seats)} asientos restantes")
        
        # Insertar horarios
        print("Generando horarios...")
        schedules = []
        for i in range(12000):
            schedules.append(generate_schedule())
            if len(schedules) >= 1000:
                insert_schedule_query = """
                INSERT INTO schedules (movie_id, room_id, show_time, price, is_active)
                VALUES (%(movie_id)s, %(room_id)s, %(show_time)s, %(price)s, %(is_active)s)
                """
                cursor.executemany(insert_schedule_query, schedules)
                connection.commit()
                print(f"✅ Insertados {len(schedules)} horarios (lote)")
                schedules = []
        if schedules:
            insert_schedule_query = """
            INSERT INTO schedules (movie_id, room_id, show_time, price, is_active)
            VALUES (%(movie_id)s, %(room_id)s, %(show_time)s, %(price)s, %(is_active)s)
            """
            cursor.executemany(insert_schedule_query, schedules)
            connection.commit()
            print(f"✅ Insertados {len(schedules)} horarios restantes")
        
        print("🚀 Datos generados exitosamente")
    except mysql.connector.Error as error:
        print(f"Error de MySQL: {error}")
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    generate_data()
