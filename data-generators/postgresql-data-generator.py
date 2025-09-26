import psycopg2
import random
import string
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
    'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores'
]

PAYMENT_METHODS = ['credit_card', 'debit_card', 'paypal', 'cash', 'bank_transfer']
PAYMENT_STATUSES = ['PENDING', 'COMPLETED', 'FAILED', 'REFUNDED']
RESERVATION_STATUSES = ['PENDING', 'CONFIRMED', 'CANCELLED', 'EXPIRED']

def generate_user():
    """Genera un usuario"""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    
    return {
        'email': f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@email.com",
        'name': f"{first_name} {last_name}",
        'phone': f"+1{random.randint(1000000000, 9999999999)}"
    }

def generate_reservation(user_id):
    """Genera una reserva"""
    # Generar fecha aleatoria en los últimos 6 meses
    start_date = datetime.now() - timedelta(days=180)
    end_date = datetime.now()
    
    random_date = start_date + timedelta(
        days=random.randint(0, (end_date - start_date).days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    
    return {
        'user_id': user_id,
        'schedule_id': random.randint(1, 12000),  # Referencia a MySQL
        'movie_id': f"507f1f77bcf86cd799{random.randint(100000, 999999)}",  # Referencia a MongoDB
        'total_amount': round(random.uniform(10.0, 100.0), 2),
        'status': random.choice(RESERVATION_STATUSES),
        'reservation_date': random_date
    }

def generate_reserved_seats(reservation_id, num_seats):
    """Genera asientos reservados para una reserva"""
    seats = []
    for _ in range(num_seats):
        seats.append({
            'reservation_id': reservation_id,
            'seat_id': random.randint(1, 15000)  # Referencia a MySQL
        })
    return seats

def generate_payment(reservation_id, amount):
    """Genera un pago para una reserva"""
    return {
        'reservation_id': reservation_id,
        'amount': amount,
        'payment_method': random.choice(PAYMENT_METHODS),
        'payment_status': random.choice(PAYMENT_STATUSES),
        'transaction_id': f"TXN{random.randint(100000000, 999999999)}"
    }

def generate_data():
    """Función principal para generar datos"""
    connection = None
    
    try:
        # Conectar a PostgreSQL
        connection = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = connection.cursor()
        
        print("Conectado a PostgreSQL")
        
        # Generar usuarios
        print("Generando usuarios...")
        users = []
        USERS_COUNT = 2000  # 2,000 usuarios
        
        for i in range(USERS_COUNT):
            users.append(generate_user())
        
        # Insertar usuarios
        insert_user_query = """
        INSERT INTO users (email, name, phone, created_at, updated_at)
        VALUES (%(email)s, %(name)s, %(phone)s, NOW(), NOW())
        RETURNING id
        """
        
        user_ids = []
        for user in users:
            cursor.execute(insert_user_query, user)
            user_id = cursor.fetchone()[0]
            user_ids.append(user_id)
        
        connection.commit()
        print(f"✅ Insertados {len(users)} usuarios")
        
        # Generar reservas
        print("Generando reservas...")
        reservations = []
        RESERVATIONS_COUNT = 15000  # 15,000 reservas
        
        for i in range(RESERVATIONS_COUNT):
            user_id = random.choice(user_ids)
            reservation = generate_reservation(user_id)
            reservations.append(reservation)
            
            # Insertar en lotes de 1000
            if len(reservations) >= 1000:
                insert_reservation_query = """
                INSERT INTO reservations (user_id, schedule_id, movie_id, total_amount, status, reservation_date)
                VALUES (%(user_id)s, %(schedule_id)s, %(movie_id)s, %(total_amount)s, %(status)s, %(reservation_date)s)
                RETURNING id
                """
                
                reservation_ids = []
                for reservation in reservations:
                    cursor.execute(insert_reservation_query, reservation)
                    reservation_id = cursor.fetchone()[0]
                    reservation_ids.append(reservation_id)
                
                connection.commit()
                print(f"✅ Insertadas {len(reservations)} reservas (lote)")
                
                # Generar asientos reservados para estas reservas
                print("Generando asientos reservados...")
                all_reserved_seats = []
                for i, reservation_id in enumerate(reservation_ids):
                    num_seats = random.randint(1, 6)  # 1-6 asientos por reserva
                    reserved_seats = generate_reserved_seats(reservation_id, num_seats)
                    all_reserved_seats.extend(reserved_seats)
                
                if all_reserved_seats:
                    insert_seats_query = """
                    INSERT INTO reserved_seats (reservation_id, seat_id)
                    VALUES (%(reservation_id)s, %(seat_id)s)
                    """
                    cursor.executemany(insert_seats_query, all_reserved_seats)
                    connection.commit()
                    print(f"✅ Insertados {len(all_reserved_seats)} asientos reservados")
                
                reservations = []
        
        # Insertar reservas restantes
        if reservations:
            insert_reservation_query = """
            INSERT INTO reservations (user_id, schedule_id, movie_id, total_amount, status, reservation_date)
            VALUES (%(user_id)s, %(schedule_id)s, %(movie_id)s, %(total_amount)s, %(status)s, %(reservation_date)s)
            RETURNING id
            """
            
            reservation_ids = []
            for reservation in reservations:
                cursor.execute(insert_reservation_query, reservation)
                reservation_id = cursor.fetchone()[0]
                reservation_ids.append(reservation_id)
            
            connection.commit()
            print(f"✅ Insertadas {len(reservations)} reservas restantes")
            
            # Generar asientos reservados para reservas restantes
            all_reserved_seats = []
            for reservation_id in reservation_ids:
                num_seats = random.randint(1, 6)
                reserved_seats = generate_reserved_seats(reservation_id, num_seats)
                all_reserved_seats.extend(reserved_seats)
            
            if all_reserved_seats:
                insert_seats_query = """
                INSERT INTO reserved_seats (reservation_id, seat_id)
                VALUES (%(reservation_id)s, %(seat_id)s)
                """
                cursor.executemany(insert_seats_query, all_reserved_seats)
                connection.commit()
                print(f"✅ Insertados {len(all_reserved_seats)} asientos reservados restantes")
        
        # Generar pagos para todas las reservas
        print("Generando pagos...")
        cursor.execute("SELECT id, total_amount FROM reservations")
        all_reservations = cursor.fetchall()
        
        payments = []
        for reservation_id, amount in all_reservations:
            payment = generate_payment(reservation_id, amount)
            payments.append(payment)
            
            # Insertar en lotes de 1000
            if len(payments) >= 1000:
                insert_payment_query = """
                INSERT INTO payments (reservation_id, amount, payment_method, payment_status, transaction_id, payment_date)
                VALUES (%(reservation_id)s, %(amount)s, %(payment_method)s, %(payment_status)s, %(transaction_id)s, NOW())
                """
                cursor.executemany(insert_payment_query, payments)
                connection.commit()
                print(f"✅ Insertados {len(payments)} pagos (lote)")
                payments = []
        
        # Insertar pagos restantes
        if payments:
            insert_payment_query = """
            INSERT INTO payments (reservation_id, amount, payment_method, payment_status, transaction_id, payment_date)
            VALUES (%(reservation_id)s, %(amount)s, %(payment_method)s, %(payment_status)s, %(transaction_id)s, NOW())
            """
            cursor.executemany(insert_payment_query, payments)
            connection.commit()
            print(f"✅ Insertados {len(payments)} pagos restantes")
        
        print(f"👥 Total de usuarios generados: {USERS_COUNT}")
        print(f"🎫 Total de reservas generadas: {RESERVATIONS_COUNT}")
        print(f"💳 Total de pagos generados: {len(all_reservations)}")
        
    except psycopg2.Error as error:
        print(f"Error de PostgreSQL: {error}")
    except Exception as error:
        print(f"Error: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Conexión cerrada")

if __name__ == "__main__":
    generate_data()