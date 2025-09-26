from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    screen_type = db.Column(db.Enum('2D', '3D', 'IMAX'), default='2D')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    seats = db.relationship('Seat', backref='room', lazy=True, cascade='all, delete-orphan')
    schedules = db.relationship('Schedule', backref='room', lazy=True, cascade='all, delete-orphan')

class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    row_number = db.Column(db.String(10), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    seat_type = db.Column(db.Enum('regular', 'premium', 'vip'), default='regular')
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('room_id', 'row_number', 'seat_number', name='unique_seat'),)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String(100), nullable=False)  # Referencia a MongoDB
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    show_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Esquemas de validación
class RoomSchema(Schema):
    name = fields.Str(required=True)
    capacity = fields.Int(required=True)
    screen_type = fields.Str(validate=lambda x: x in ['2D', '3D', 'IMAX'])

class SeatSchema(Schema):
    row_number = fields.Str(required=True)
    seat_number = fields.Int(required=True)
    seat_type = fields.Str(validate=lambda x: x in ['regular', 'premium', 'vip'])

class ScheduleSchema(Schema):
    movie_id = fields.Str(required=True)
    room_id = fields.Int(required=True)
    show_time = fields.DateTime(required=True)
    price = fields.Decimal(required=True)

# Schemas para serialización
room_schema = RoomSchema()
rooms_schema = RoomSchema(many=True)
seat_schema = SeatSchema()
seats_schema = SeatSchema(many=True)
schedule_schema = ScheduleSchema()
schedules_schema = ScheduleSchema(many=True)

# Rutas para Salas
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    try:
        rooms = Room.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'data': [{
                'id': room.id,
                'name': room.name,
                'capacity': room.capacity,
                'screen_type': room.screen_type,
                'is_active': room.is_active,
                'created_at': room.created_at.isoformat()
            } for room in rooms]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
def get_room(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        return jsonify({
            'success': True,
            'data': {
                'id': room.id,
                'name': room.name,
                'capacity': room.capacity,
                'screen_type': room.screen_type,
                'is_active': room.is_active,
                'created_at': room.created_at.isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms', methods=['POST'])
def create_room():
    try:
        data = request.get_json()
        errors = room_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': 'Validation error', 'details': errors}), 400
        
        room = Room(**data)
        db.session.add(room)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': room.id,
                'name': room.name,
                'capacity': room.capacity,
                'screen_type': room.screen_type,
                'is_active': room.is_active,
                'created_at': room.created_at.isoformat()
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Rutas para Asientos
@app.route('/api/rooms/<int:room_id>/seats', methods=['GET'])
def get_room_seats(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        seats = Seat.query.filter_by(room_id=room_id).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': seat.id,
                'room_id': seat.room_id,
                'row_number': seat.row_number,
                'seat_number': seat.seat_number,
                'seat_type': seat.seat_type,
                'is_available': seat.is_available
            } for seat in seats]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/rooms/<int:room_id>/seats', methods=['POST'])
def create_seats(room_id):
    try:
        room = Room.query.get_or_404(room_id)
        data = request.get_json()
        
        # Crear asientos automáticamente basado en la capacidad
        if 'auto_generate' in data and data['auto_generate']:
            seats_per_row = data.get('seats_per_row', 10)
            rows = room.capacity // seats_per_row
            
            for row in range(1, rows + 1):
                for seat_num in range(1, seats_per_row + 1):
                    seat = Seat(
                        room_id=room_id,
                        row_number=chr(64 + row),  # A, B, C, etc.
                        seat_number=seat_num,
                        seat_type='regular'
                    )
                    db.session.add(seat)
        else:
            # Crear asientos individuales
            for seat_data in data['seats']:
                errors = seat_schema.validate(seat_data)
                if errors:
                    return jsonify({'success': False, 'error': 'Validation error', 'details': errors}), 400
                
                seat = Seat(room_id=room_id, **seat_data)
                db.session.add(seat)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Seats created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Rutas para Horarios
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    try:
        movie_id = request.args.get('movie_id')
        room_id = request.args.get('room_id')
        
        query = Schedule.query.filter_by(is_active=True)
        
        if movie_id:
            query = query.filter_by(movie_id=movie_id)
        if room_id:
            query = query.filter_by(room_id=room_id)
        
        schedules = query.all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': schedule.id,
                'movie_id': schedule.movie_id,
                'room_id': schedule.room_id,
                'show_time': schedule.show_time.isoformat(),
                'price': float(schedule.price),
                'is_active': schedule.is_active,
                'room_name': schedule.room.name
            } for schedule in schedules]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    try:
        data = request.get_json()
        errors = schedule_schema.validate(data)
        if errors:
            return jsonify({'success': False, 'error': 'Validation error', 'details': errors}), 400
        
        schedule = Schedule(**data)
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': schedule.id,
                'movie_id': schedule.movie_id,
                'room_id': schedule.room_id,
                'show_time': schedule.show_time.isoformat(),
                'price': float(schedule.price),
                'is_active': schedule.is_active
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/schedules/movie/<movie_id>', methods=['GET'])
def get_schedules_by_movie(movie_id):
    try:
        schedules = Schedule.query.filter_by(movie_id=movie_id, is_active=True).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': schedule.id,
                'movie_id': schedule.movie_id,
                'room_id': schedule.room_id,
                'show_time': schedule.show_time.isoformat(),
                'price': float(schedule.price),
                'room_name': schedule.room.name,
                'room_capacity': schedule.room.capacity
            } for schedule in schedules]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Health check
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'rooms-api'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3002)), debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true')