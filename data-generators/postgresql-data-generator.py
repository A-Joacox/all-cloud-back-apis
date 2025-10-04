import psycopg2
import random
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de conexión
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'user': os.getenv('POSTGRES_USER', 'cinema_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'cinema_password'),
    'database': os.getenv('POSTGRES_DATABASE', 'cinema_reservations')
}

# Datos de ejemplo
FIRST_NAMES = [
    'John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Emily',
    'James', 'Jessica', 'William', 'Ashley', 'Richard', 'Amanda', 'Charles',
    'Jennifer', 'Joseph', 'Michelle', 'Thomas', 'Kimberly', 'Christopher',
    'Donna', 'Daniel', 'Carol', 'Paul', 'Sandra', 'Mark', 'Ruth', 'Donald',
    'Sharon', 'Steven', 'Laura', 'Andrew', 'Helen', 'Joshua', 'Deborah'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
    'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
    'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
    'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
    'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Pork'
]

PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'cash', 'bank_transfer']
PAYMENT_STATUSES = ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']
RESERVATION_STATUSES = ['PENDING', 'CONFIRMED', 'CANCELLED', 'EXPIRED']

def create_tables_if_not_exist(cursor):
    """Crear tablas si no existen"""
    print("🔧 Verificando y creando tablas si es necesario...")
    
    # Tabla users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabla reservations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            schedule_id INTEGER NOT NULL,
            movie_id VARCHAR(100) NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING',
            reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Tabla reserved_seats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserved_seats (
            id SERIAL PRIMARY KEY,
            reservation_id INTEGER NOT NULL,
            seat_id INTEGER NOT NULL,
            FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
        )
    """)
    
    # Tabla payments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id SERIAL PRIMARY KEY,
            reservation_id INTEGER NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            payment_status VARCHAR(20) DEFAULT 'PENDING',
            transaction_id VARCHAR(255),
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
        )
    """)
    
    print("✅ Tablas verificadas/creadas correctamente")

def generate_user():
    """Genera un usuario"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    return {
        'email': f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 9999)}@email.com",
        'name': f"{first_name} {last_name}",
        'phone': f"+1{random.randint(1000000000, 9999999999)}"
    }

def generate_reservation(user_id):
    """Genera una reserva"""
    start_date = datetime.now() - timedelta(days=180)
    end_date = datetime.now()
    
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    
    return {
        'user_id': user_id,
        'schedule_id': random.randint(1, 12000),
        'movie_id': f"507f1f77bcf86cd799{random.randint(100000, 999999)}",
        'total_amount': round(random.uniform(10.0, 100.0), 2),
        'status': random.choice(RESERVATION_STATUSES),
        'reservation_date': random_date
    }

def generate_reserved_seats(reservation_id, num_seats):
    seats = []
    for _ in range(num_seats):
        seats.append({
            'reservation_id': reservation_id,
            'seat_id': random.randint(1, 15000)
        })
    return seats

def generate_payment(reservation_id, amount):
    return {
        'reservation_id': reservation_id,
        'amount': amount,
        'payment_method': random.choice(PAYMENT_METHODS),
        'payment_status': random.choice(PAYMENT_STATUSES),
        'transaction_id': f"TXN{random.randint(100000000, 999999999)}"
    }

def generate_data():
    connection = None
    try:
        connection = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = connection.cursor()
        print("Conectado a PostgreSQL")
        
        # Crear tablas si no existen
        create_tables_if_not_exist(cursor)
        connection.commit()
        
        print("Generando usuarios...")
        users = [generate_user() for _ in range(2000)]
        
        insert_user_query = """
        INSERT INTO users (email, name, phone, created_at, updated_at)
        VALUES (%(email)s, %(name)s, %(phone)s, NOW(), NOW())
        ON CONFLICT (email) DO NOTHING
        RETURNING id
        """
        
        user_ids = []
        for user in users:
            cursor.execute(insert_user_query, user)
            res = cursor.fetchone()
            if res:
                user_ids.append(res[0])
        
        connection.commit()
        print(f"✅ Insertados {len(user_ids)} usuarios únicos")
        
        print("Generando reservas...")
        reservations = []
        RESERVATIONS_COUNT = 15000
        
        for i in range(RESERVATIONS_COUNT):
            user_id = random.choice(user_ids)
            reservation = generate_reservation(user_id)
            reservations.append(reservation)
            
            if len(reservations) >= 1000:
                insert_reservation_query = """
                INSERT INTO reservations (user_id, schedule_id, movie_id, total_amount, status, reservation_date)
                VALUES (%(user_id)s, %(schedule_id)s, %(movie_id)s, %(total_amount)s, %(status)s, %(reservation_date)s)
                RETURNING id
                """
                reservation_ids = []
                for reservation in reservations:
                    cursor.execute(insert_reservation_query, reservation)
                    res = cursor.fetchone()
                    if res:
                        reservation_ids.append(res[0])
                connection.commit()
                print(f"✅ Insertadas {len(reservations)} reservas (lote)")
                
                all_reserved_seats = []
                for reservation_id in reservation_ids:
                    num_seats = random.randint(1, 6)
                    all_reserved_seats.extend(generate_reserved_seats(reservation_id, num_seats))
                
                if all_reserved_seats:
                    cursor.executemany("""
                        INSERT INTO reserved_seats (reservation_id, seat_id)
                        VALUES (%(reservation_id)s, %(seat_id)s)
                    """, all_reserved_seats)
                    connection.commit()
                    print(f"✅ Insertados {len(all_reserved_seats)} asientos reservados")
                
                reservations = []
        
        print("Generando pagos...")
        cursor.execute("SELECT id, total_amount FROM reservations")
        all_reservations = cursor.fetchall()
        
        payments = []
        for reservation_id, amount in all_reservations:
            payments.append(generate_payment(reservation_id, amount))
            if len(payments) >= 1000:
                cursor.executemany("""
                    INSERT INTO payments (reservation_id, amount, payment_method, payment_status, transaction_id, payment_date)
                    VALUES (%(reservation_id)s, %(amount)s, %(payment_method)s, %(payment_status)s, %(transaction_id)s, NOW())
                """, payments)
                connection.commit()
                print(f"✅ Insertados {len(payments)} pagos (lote)")
                payments = []
        
        if payments:
            cursor.executemany("""
                INSERT INTO payments (reservation_id, amount, payment_method, payment_status, transaction_id, payment_date)
                VALUES (%(reservation_id)s, %(amount)s, %(payment_method)s, %(payment_status)s, %(transaction_id)s, NOW())
            """, payments)
            connection.commit()
            print(f"✅ Insertados {len(payments)} pagos restantes")
        
        print(f"👥 Total de usuarios generados: {len(user_ids)}")
        print(f"🎫 Total de reservas generadas: {RESERVATIONS_COUNT}")
        print(f"💳 Total de pagos generados: {len(all_reservations)}")
    
    except psycopg2.Error as error:
        print(f"Error de PostgreSQL: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    generate_data()
