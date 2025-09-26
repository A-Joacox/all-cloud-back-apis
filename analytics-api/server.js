const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const axios = require('axios');
const moment = require('moment');
const _ = require('lodash');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3005;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// URLs de los microservicios
const MOVIES_API_URL = process.env.MOVIES_API_URL || 'http://localhost:3001';
const ROOMS_API_URL = process.env.ROOMS_API_URL || 'http://localhost:3002';
const RESERVATIONS_API_URL = process.env.RESERVATIONS_API_URL || 'http://localhost:3003';

// Función helper para hacer requests a otros servicios
const makeRequest = async (url, method = 'GET', data = null) => {
  try {
    const config = {
      method,
      url,
      headers: {
        'Content-Type': 'application/json'
      }
    };
    
    if (data) {
      config.data = data;
    }
    
    const response = await axios(config);
    return response.data;
  } catch (error) {
    console.error(`Error calling ${url}:`, error.message);
    throw new Error(`Service unavailable: ${error.message}`);
  }
};

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'analytics-api',
    timestamp: new Date().toISOString()
  });
});

// ===== ANÁLISIS DE INGRESOS =====

// GET /api/analytics/revenue - Análisis de ingresos
app.get('/api/analytics/revenue', async (req, res) => {
  try {
    const { period = 'month', startDate, endDate } = req.query;
    
    // Obtener todas las reservas
    const reservationsResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/reservations`);
    if (!reservationsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch reservations' });
    }
    
    const reservations = reservationsResponse.data;
    let filteredReservations = reservations;
    
    // Filtrar por fechas si se proporcionan
    if (startDate && endDate) {
      const start = moment(startDate);
      const end = moment(endDate);
      filteredReservations = reservations.filter(reservation => {
        const reservationDate = moment(reservation.reservationDate);
        return reservationDate.isBetween(start, end, null, '[]');
      });
    }
    
    // Calcular métricas de ingresos
    const totalRevenue = _.sumBy(filteredReservations, 'totalAmount');
    const totalReservations = filteredReservations.length;
    const averageTicketPrice = totalReservations > 0 ? totalRevenue / totalReservations : 0;
    
    // Agrupar por período
    let groupedRevenue;
    switch (period) {
      case 'day':
        groupedRevenue = _.groupBy(filteredReservations, reservation => 
          moment(reservation.reservationDate).format('YYYY-MM-DD')
        );
        break;
      case 'week':
        groupedRevenue = _.groupBy(filteredReservations, reservation => 
          moment(reservation.reservationDate).format('YYYY-[W]WW')
        );
        break;
      case 'month':
        groupedRevenue = _.groupBy(filteredReservations, reservation => 
          moment(reservation.reservationDate).format('YYYY-MM')
        );
        break;
      case 'year':
        groupedRevenue = _.groupBy(filteredReservations, reservation => 
          moment(reservation.reservationDate).format('YYYY')
        );
        break;
      default:
        groupedRevenue = { 'all': filteredReservations };
    }
    
    // Calcular ingresos por período
    const revenueByPeriod = Object.keys(groupedRevenue).map(periodKey => {
      const periodReservations = groupedRevenue[periodKey];
      const periodRevenue = _.sumBy(periodReservations, 'totalAmount');
      return {
        period: periodKey,
        revenue: periodRevenue,
        reservations: periodReservations.length,
        averageTicketPrice: periodReservations.length > 0 ? periodRevenue / periodReservations.length : 0
      };
    });
    
    res.json({
      success: true,
      data: {
        summary: {
          totalRevenue,
          totalReservations,
          averageTicketPrice
        },
        revenueByPeriod: _.orderBy(revenueByPeriod, 'revenue', 'desc')
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== PELÍCULAS MÁS POPULARES =====

// GET /api/analytics/popular-movies - Películas más populares
app.get('/api/analytics/popular-movies', async (req, res) => {
  try {
    const { limit = 10, period = 'month' } = req.query;
    
    // Obtener todas las reservas
    const reservationsResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/reservations`);
    if (!reservationsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch reservations' });
    }
    
    const reservations = reservationsResponse.data;
    
    // Filtrar por período si es necesario
    let filteredReservations = reservations;
    if (period !== 'all') {
      const cutoffDate = moment().subtract(1, period).toDate();
      filteredReservations = reservations.filter(reservation => 
        new Date(reservation.reservationDate) >= cutoffDate
      );
    }
    
    // Agrupar por película
    const movieStats = _.groupBy(filteredReservations, 'movieId');
    
    // Obtener información de películas
    const movieDetails = await Promise.all(
      Object.keys(movieStats).map(async (movieId) => {
        try {
          const movieResponse = await makeRequest(`${MOVIES_API_URL}/api/movies/${movieId}`);
          return movieResponse.success ? movieResponse.data : null;
        } catch (error) {
          console.error(`Error fetching movie ${movieId}:`, error.message);
          return null;
        }
      })
    );
    
    // Calcular estadísticas por película
    const popularMovies = Object.keys(movieStats).map((movieId, index) => {
      const movieReservations = movieStats[movieId];
      const movieDetails = movieDetails[index];
      
      return {
        movieId,
        title: movieDetails?.title || 'Unknown Movie',
        totalReservations: movieReservations.length,
        totalRevenue: _.sumBy(movieReservations, 'totalAmount'),
        averageTicketPrice: movieReservations.length > 0 ? 
          _.sumBy(movieReservations, 'totalAmount') / movieReservations.length : 0
      };
    });
    
    // Ordenar por popularidad (número de reservas)
    const sortedMovies = _.orderBy(popularMovies, 'totalReservations', 'desc');
    
    res.json({
      success: true,
      data: sortedMovies.slice(0, parseInt(limit))
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== OCUPACIÓN DE SALAS =====

// GET /api/analytics/occupancy - Ocupación de salas
app.get('/api/analytics/occupancy', async (req, res) => {
  try {
    const { period = 'week', roomId } = req.query;
    
    // Obtener todas las salas
    const roomsResponse = await makeRequest(`${ROOMS_API_URL}/api/rooms`);
    if (!roomsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch rooms' });
    }
    
    const rooms = roomsResponse.data;
    let filteredRooms = rooms;
    
    if (roomId) {
      filteredRooms = rooms.filter(room => room.id === parseInt(roomId));
    }
    
    // Obtener todas las reservas
    const reservationsResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/reservations`);
    if (!reservationsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch reservations' });
    }
    
    const reservations = reservationsResponse.data;
    
    // Filtrar por período
    let filteredReservations = reservations;
    if (period !== 'all') {
      const cutoffDate = moment().subtract(1, period).toDate();
      filteredReservations = reservations.filter(reservation => 
        new Date(reservation.reservationDate) >= cutoffDate
      );
    }
    
    // Calcular ocupación por sala
    const occupancyStats = await Promise.all(
      filteredRooms.map(async (room) => {
        try {
          // Obtener asientos de la sala
          const seatsResponse = await makeRequest(`${ROOMS_API_URL}/api/rooms/${room.id}/seats`);
          const totalSeats = seatsResponse.success ? seatsResponse.data.length : 0;
          
          // Obtener horarios de la sala
          const schedulesResponse = await makeRequest(`${ROOMS_API_URL}/api/schedules?room_id=${room.id}`);
          const schedules = schedulesResponse.success ? schedulesResponse.data : [];
          
          // Filtrar horarios por período
          let filteredSchedules = schedules;
          if (period !== 'all') {
            const cutoffDate = moment().subtract(1, period).toDate();
            filteredSchedules = schedules.filter(schedule => 
              new Date(schedule.show_time) >= cutoffDate
            );
          }
          
          // Calcular asientos ocupados
          const roomReservations = reservations.filter(reservation => 
            filteredSchedules.some(schedule => schedule.id === reservation.scheduleId)
          );
          
          const occupiedSeats = _.sumBy(roomReservations, reservation => 
            reservation.reservedSeats ? reservation.reservedSeats.length : 0
          );
          
          const totalPossibleSeats = totalSeats * filteredSchedules.length;
          const occupancyRate = totalPossibleSeats > 0 ? (occupiedSeats / totalPossibleSeats) * 100 : 0;
          
          return {
            roomId: room.id,
            roomName: room.name,
            totalSeats,
            totalSchedules: filteredSchedules.length,
            occupiedSeats,
            totalPossibleSeats,
            occupancyRate: Math.round(occupancyRate * 100) / 100
          };
        } catch (error) {
          console.error(`Error calculating occupancy for room ${room.id}:`, error.message);
          return {
            roomId: room.id,
            roomName: room.name,
            totalSeats: 0,
            totalSchedules: 0,
            occupiedSeats: 0,
            totalPossibleSeats: 0,
            occupancyRate: 0
          };
        }
      })
    );
    
    // Calcular estadísticas generales
    const totalOccupiedSeats = _.sumBy(occupancyStats, 'occupiedSeats');
    const totalPossibleSeats = _.sumBy(occupancyStats, 'totalPossibleSeats');
    const overallOccupancyRate = totalPossibleSeats > 0 ? 
      (totalOccupiedSeats / totalPossibleSeats) * 100 : 0;
    
    res.json({
      success: true,
      data: {
        summary: {
          totalRooms: filteredRooms.length,
          totalOccupiedSeats,
          totalPossibleSeats,
          overallOccupancyRate: Math.round(overallOccupancyRate * 100) / 100
        },
        roomOccupancy: _.orderBy(occupancyStats, 'occupancyRate', 'desc')
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== COMPORTAMIENTO DE USUARIOS =====

// GET /api/analytics/user-behavior - Comportamiento de usuarios
app.get('/api/analytics/user-behavior', async (req, res) => {
  try {
    const { period = 'month' } = req.query;
    
    // Obtener todos los usuarios
    const usersResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/users`);
    if (!usersResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch users' });
    }
    
    const users = usersResponse.data;
    
    // Obtener todas las reservas
    const reservationsResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/reservations`);
    if (!reservationsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch reservations' });
    }
    
    const reservations = reservationsResponse.data;
    
    // Filtrar por período
    let filteredReservations = reservations;
    if (period !== 'all') {
      const cutoffDate = moment().subtract(1, period).toDate();
      filteredReservations = reservations.filter(reservation => 
        new Date(reservation.reservationDate) >= cutoffDate
      );
    }
    
    // Calcular métricas de comportamiento
    const userBehaviorStats = users.map(user => {
      const userReservations = filteredReservations.filter(reservation => 
        reservation.userId === user.id
      );
      
      const totalSpent = _.sumBy(userReservations, 'totalAmount');
      const averageTicketPrice = userReservations.length > 0 ? 
        totalSpent / userReservations.length : 0;
      
      return {
        userId: user.id,
        userName: user.name,
        totalReservations: userReservations.length,
        totalSpent,
        averageTicketPrice,
        lastReservationDate: userReservations.length > 0 ? 
          _.maxBy(userReservations, 'reservationDate')?.reservationDate : null
      };
    });
    
    // Calcular estadísticas generales
    const activeUsers = userBehaviorStats.filter(user => user.totalReservations > 0);
    const totalRevenue = _.sumBy(activeUsers, 'totalSpent');
    const averageSpendingPerUser = activeUsers.length > 0 ? 
      totalRevenue / activeUsers.length : 0;
    
    // Segmentar usuarios por comportamiento
    const userSegments = {
      vip: activeUsers.filter(user => user.totalSpent >= 200),
      regular: activeUsers.filter(user => user.totalSpent >= 50 && user.totalSpent < 200),
      casual: activeUsers.filter(user => user.totalSpent < 50),
      inactive: userBehaviorStats.filter(user => user.totalReservations === 0)
    };
    
    res.json({
      success: true,
      data: {
        summary: {
          totalUsers: users.length,
          activeUsers: activeUsers.length,
          totalRevenue,
          averageSpendingPerUser: Math.round(averageSpendingPerUser * 100) / 100
        },
        userSegments: {
          vip: userSegments.vip.length,
          regular: userSegments.regular.length,
          casual: userSegments.casual.length,
          inactive: userSegments.inactive.length
        },
        topUsers: _.orderBy(activeUsers, 'totalSpent', 'desc').slice(0, 10)
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== MÉTRICAS GENERALES =====

// GET /api/analytics/dashboard - Dashboard con métricas generales
app.get('/api/analytics/dashboard', async (req, res) => {
  try {
    const { period = 'month' } = req.query;
    
    // Obtener datos de todos los servicios
    const [moviesResponse, roomsResponse, usersResponse, reservationsResponse] = await Promise.all([
      makeRequest(`${MOVIES_API_URL}/api/movies`),
      makeRequest(`${ROOMS_API_URL}/api/rooms`),
      makeRequest(`${RESERVATIONS_API_URL}/api/users`),
      makeRequest(`${RESERVATIONS_API_URL}/api/reservations`)
    ]);
    
    if (!moviesResponse.success || !roomsResponse.success || 
        !usersResponse.success || !reservationsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch data from services' });
    }
    
    const movies = moviesResponse.data;
    const rooms = roomsResponse.data;
    const users = usersResponse.data;
    const reservations = reservationsResponse.data;
    
    // Filtrar reservas por período
    let filteredReservations = reservations;
    if (period !== 'all') {
      const cutoffDate = moment().subtract(1, period).toDate();
      filteredReservations = reservations.filter(reservation => 
        new Date(reservation.reservationDate) >= cutoffDate
      );
    }
    
    // Calcular métricas
    const totalRevenue = _.sumBy(filteredReservations, 'totalAmount');
    const totalReservations = filteredReservations.length;
    const averageTicketPrice = totalReservations > 0 ? totalRevenue / totalReservations : 0;
    
    // Películas más populares
    const movieStats = _.groupBy(filteredReservations, 'movieId');
    const popularMovies = Object.keys(movieStats).map(movieId => ({
      movieId,
      reservations: movieStats[movieId].length
    }));
    const topMovies = _.orderBy(popularMovies, 'reservations', 'desc').slice(0, 5);
    
    res.json({
      success: true,
      data: {
        overview: {
          totalMovies: movies.length,
          totalRooms: rooms.length,
          totalUsers: users.length,
          totalReservations,
          totalRevenue: Math.round(totalRevenue * 100) / 100,
          averageTicketPrice: Math.round(averageTicketPrice * 100) / 100
        },
        topMovies: topMovies,
        period: period
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Analytics error:', error);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error' 
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    success: false, 
    error: 'Endpoint not found' 
  });
});

app.listen(PORT, () => {
  console.log(`Analytics API running on port ${PORT}`);
  console.log(`Movies API: ${MOVIES_API_URL}`);
  console.log(`Rooms API: ${ROOMS_API_URL}`);
  console.log(`Reservations API: ${RESERVATIONS_API_URL}`);
});