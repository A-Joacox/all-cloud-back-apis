const { MongoClient } = require('mongodb');
const mysql = require('mysql2/promise');
const { Client } = require('pg');

// Configuración de conexiones
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/cinema_movies';
const MYSQL_CONFIG = {
    host: process.env.MYSQL_HOST || 'localhost',
    port: parseInt(process.env.MYSQL_PORT) || 3307,
    user: process.env.MYSQL_USER || 'cinema_user',
    password: process.env.MYSQL_PASSWORD || 'cinema_password',
    database: process.env.MYSQL_DATABASE || 'cinema_rooms'
};
const POSTGRES_CONFIG = {
    host: process.env.POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.POSTGRES_PORT) || 5432,
    user: process.env.POSTGRES_USER || 'cinema_user',
    password: process.env.POSTGRES_PASSWORD || 'cinema_password',
    database: process.env.POSTGRES_DATABASE || 'cinema_reservations'
};

async function verifyMongoDB() {
    console.log('🔍 Verificando MongoDB...');
    try {
        const client = new MongoClient(MONGODB_URI);
        await client.connect();
        
        const db = client.db('cinema_movies');
        
        const moviesCount = await db.collection('movies').countDocuments();
        const genresCount = await db.collection('genres').countDocuments();
        const activeMoviesCount = await db.collection('movies').countDocuments({ isActive: true });
        
        console.log(`✅ MongoDB - Películas: ${moviesCount}`);
        console.log(`✅ MongoDB - Géneros: ${genresCount}`);
        console.log(`✅ MongoDB - Películas activas: ${activeMoviesCount}`);
        
        await client.close();
        return { movies: moviesCount, genres: genresCount, activeMovies: activeMoviesCount };
    } catch (error) {
        console.error('❌ Error verificando MongoDB:', error.message);
        return null;
    }
}

async function verifyMySQL() {
    console.log('🔍 Verificando MySQL...');
    try {
        const connection = await mysql.createConnection(MYSQL_CONFIG);
        
        const [roomsResult] = await connection.execute('SELECT COUNT(*) as count FROM rooms');
        const [seatsResult] = await connection.execute('SELECT COUNT(*) as count FROM seats');
        const [schedulesResult] = await connection.execute('SELECT COUNT(*) as count FROM schedules');
        const [activeRoomsResult] = await connection.execute('SELECT COUNT(*) as count FROM rooms WHERE is_active = true');
        
        console.log(`✅ MySQL - Salas: ${roomsResult[0].count}`);
        console.log(`✅ MySQL - Asientos: ${seatsResult[0].count}`);
        console.log(`✅ MySQL - Horarios: ${schedulesResult[0].count}`);
        console.log(`✅ MySQL - Salas activas: ${activeRoomsResult[0].count}`);
        
        await connection.end();
        return { 
            rooms: roomsResult[0].count, 
            seats: seatsResult[0].count, 
            schedules: schedulesResult[0].count,
            activeRooms: activeRoomsResult[0].count
        };
    } catch (error) {
        console.error('❌ Error verificando MySQL:', error.message);
        return null;
    }
}

async function verifyPostgreSQL() {
    console.log('🔍 Verificando PostgreSQL...');
    try {
        const client = new Client(POSTGRES_CONFIG);
        await client.connect();
        
        const usersResult = await client.query('SELECT COUNT(*) as count FROM users');
        const reservationsResult = await client.query('SELECT COUNT(*) as count FROM reservations');
        const paymentsResult = await client.query('SELECT COUNT(*) as count FROM payments');
        const reservedSeatsResult = await client.query('SELECT COUNT(*) as count FROM reserved_seats');
        
        console.log(`✅ PostgreSQL - Usuarios: ${usersResult.rows[0].count}`);
        console.log(`✅ PostgreSQL - Reservas: ${reservationsResult.rows[0].count}`);
        console.log(`✅ PostgreSQL - Pagos: ${paymentsResult.rows[0].count}`);
        console.log(`✅ PostgreSQL - Asientos reservados: ${reservedSeatsResult.rows[0].count}`);
        
        await client.end();
        return { 
            users: usersResult.rows[0].count, 
            reservations: reservationsResult.rows[0].count, 
            payments: paymentsResult.rows[0].count,
            reservedSeats: reservedSeatsResult.rows[0].count
        };
    } catch (error) {
        console.error('❌ Error verificando PostgreSQL:', error.message);
        return null;
    }
}

async function verifyAll() {
    console.log('🚀 Iniciando verificación de datos...\n');
    
    const mongoResults = await verifyMongoDB();
    console.log('');
    
    const mysqlResults = await verifyMySQL();
    console.log('');
    
    const postgresResults = await verifyPostgreSQL();
    console.log('');
    
    // Resumen total
    console.log('📊 RESUMEN TOTAL:');
    console.log('================');
    
    if (mongoResults) {
        console.log(`🎬 MongoDB: ${mongoResults.movies} películas, ${mongoResults.genres} géneros`);
    }
    
    if (mysqlResults) {
        console.log(`🏢 MySQL: ${mysqlResults.rooms} salas, ${mysqlResults.seats} asientos, ${mysqlResults.schedules} horarios`);
    }
    
    if (postgresResults) {
        console.log(`👥 PostgreSQL: ${postgresResults.users} usuarios, ${postgresResults.reservations} reservas, ${postgresResults.payments} pagos`);
    }
    
    // Calcular total
    const totalRecords = (mongoResults?.movies || 0) + 
                        (mysqlResults?.seats || 0) + 
                        (postgresResults?.reservations || 0);
    
    console.log(`\n🎯 Total de registros generados: ${totalRecords.toLocaleString()}`);
    
    if (totalRecords >= 20000) {
        console.log('✅ ¡Objetivo de 20,000 registros alcanzado!');
    } else {
        console.log('⚠️  Objetivo de 20,000 registros no alcanzado');
    }
}

// Ejecutar verificación
if (require.main === module) {
    verifyAll().catch(console.error);
}

module.exports = { verifyAll, verifyMongoDB, verifyMySQL, verifyPostgreSQL };