-- PostgreSQL Schema for Reservations API
-- Database: cinema_reservations

CREATE DATABASE cinema_reservations;

-- Conectar a la base de datos
\c cinema_reservations;

-- Tabla de Usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Reservas
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    schedule_id INTEGER NOT NULL, -- Referencia a MySQL
    movie_id VARCHAR(100) NOT NULL, -- Referencia a MongoDB
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tabla de Asientos Reservados
CREATE TABLE reserved_seats (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER NOT NULL,
    seat_id INTEGER NOT NULL, -- Referencia a MySQL
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
);

-- Tabla de Pagos
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    reservation_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'PENDING',
    transaction_id VARCHAR(255),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE
);

-- Índices para mejorar performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_reservations_user ON reservations(user_id);
CREATE INDEX idx_reservations_movie ON reservations(movie_id);
CREATE INDEX idx_reservations_schedule ON reservations(schedule_id);
CREATE INDEX idx_reservations_status ON reservations(status);
CREATE INDEX idx_reservations_date ON reservations(reservation_date);
CREATE INDEX idx_reserved_seats_reservation ON reserved_seats(reservation_id);
CREATE INDEX idx_payments_reservation ON payments(reservation_id);
CREATE INDEX idx_payments_status ON payments(payment_status);

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para actualizar updated_at en users
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Datos de ejemplo
INSERT INTO users (email, name, phone) VALUES
('john.doe@email.com', 'John Doe', '+1234567890'),
('jane.smith@email.com', 'Jane Smith', '+1234567891'),
('bob.wilson@email.com', 'Bob Wilson', '+1234567892'),
('alice.brown@email.com', 'Alice Brown', '+1234567893');

-- Ejemplo de reserva
INSERT INTO reservations (user_id, schedule_id, movie_id, total_amount, status) VALUES
(1, 1, '507f1f77bcf86cd799439011', 45.00, 'CONFIRMED'),
(2, 2, '507f1f77bcf86cd799439012', 30.00, 'PENDING'),
(3, 1, '507f1f77bcf86cd799439011', 60.00, 'CONFIRMED');

-- Ejemplo de asientos reservados
INSERT INTO reserved_seats (reservation_id, seat_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 10), (2, 11),
(3, 5), (3, 6), (3, 7), (3, 8);

-- Ejemplo de pagos
INSERT INTO payments (reservation_id, amount, payment_method, payment_status, transaction_id) VALUES
(1, 45.00, 'credit_card', 'COMPLETED', 'TXN123456789'),
(2, 30.00, 'debit_card', 'PENDING', 'TXN123456790'),
(3, 60.00, 'credit_card', 'COMPLETED', 'TXN123456791');