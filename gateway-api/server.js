const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const axios = require('axios');
const swaggerUi = require('swagger-ui-express');
const swaggerSpecs = require('./swagger.config');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3004;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());

// Swagger UI setup
app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpecs, {
  explorer: true,
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: "Cinema Gateway API Documentation"
}));

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

/**
 * @swagger
 * /health:
 *   get:
 *     summary: Gateway health check
 *     description: Check if the API Gateway is healthy and responsive
 *     tags: [Health]
 *     responses:
 *       200:
 *         description: Gateway is healthy
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: healthy
 *                 service:
 *                   type: string
 *                   example: gateway-api
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 */
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'gateway-api',
    timestamp: new Date().toISOString()
  });
});

// ===== ENDPOINTS ORQUESTADOS =====

/**
 * @swagger
 * /api/showtimes:
 *   get:
 *     summary: Get enriched showtimes
 *     description: Retrieve showtimes with complete movie and room information (orchestrated from multiple services)
 *     tags: [System]
 *     parameters:
 *       - in: query
 *         name: movieId
 *         schema:
 *           type: string
 *         description: Filter by movie ID
 *       - in: query
 *         name: roomId
 *         schema:
 *           type: integer
 *         description: Filter by room ID
 *       - in: query
 *         name: date
 *         schema:
 *           type: string
 *           format: date
 *         description: Filter by date (YYYY-MM-DD)
 *     responses:
 *       200:
 *         description: Enriched showtimes retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/SuccessResponse'
 *       500:
 *         description: Service error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.get('/api/showtimes', async (req, res) => {
  try {
    const { movieId, roomId, date, limit = 100 } = req.query;
    
    // Obtener horarios del servicio de salas con límite
    let schedulesUrl = `${ROOMS_API_URL}/api/schedules`;
    const scheduleParams = new URLSearchParams();
    
    if (movieId) scheduleParams.append('movie_id', movieId);
    if (roomId) scheduleParams.append('room_id', roomId);
    scheduleParams.append('limit', limit); // Agregar límite
    
    if (scheduleParams.toString()) {
      schedulesUrl += `?${scheduleParams.toString()}`;
    }
    
    const schedules = await makeRequest(schedulesUrl);
    
    if (!schedules.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch schedules' });
    }
    
    // Enriquecer con información de películas y salas
    const enrichedSchedules = await Promise.all(
      schedules.data.map(async (schedule) => {
        try {
          // Obtener información de la película
          const movieResponse = await makeRequest(`${MOVIES_API_URL}/api/movies/${schedule.movie_id}`);
          const movie = movieResponse.success ? movieResponse.data : null;
          
          // Obtener información de la sala
          const roomResponse = await makeRequest(`${ROOMS_API_URL}/api/rooms/${schedule.room_id}`);
          const room = roomResponse.success ? roomResponse.data : null;
          
          return {
            ...schedule,
            movie,
            room
          };
        } catch (error) {
          console.error(`Error enriching schedule ${schedule.id}:`, error.message);
          return schedule;
        }
      })
    );
    
    res.json({
      success: true,
      data: enrichedSchedules
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

/**
 * @swagger
 * /api/book-ticket:
 *   post:
 *     summary: Book a movie ticket
 *     description: Complete ticket booking orchestration across reservations, rooms, and movies services
 *     tags: [System]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - userId
 *               - scheduleId
 *               - movieId
 *               - seatIds
 *               - totalAmount
 *             properties:
 *               userId:
 *                 type: integer
 *                 description: User ID
 *               scheduleId:
 *                 type: integer
 *                 description: Schedule ID
 *               movieId:
 *                 type: string
 *                 description: Movie ID (MongoDB ObjectId)
 *               seatIds:
 *                 type: array
 *                 items:
 *                   type: string
 *                 description: Array of seat IDs to book
 *               totalAmount:
 *                 type: number
 *                 format: float
 *                 description: Total booking amount
 *     responses:
 *       201:
 *         description: Ticket booked successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/SuccessResponse'
 *       400:
 *         description: Bad request
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 *       500:
 *         description: Service error
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ErrorResponse'
 */
app.post('/api/book-ticket', async (req, res) => {
  try {
    const { userId, scheduleId, movieId, seatIds, totalAmount } = req.body;
    
    // Validar que el horario existe
    const scheduleResponse = await makeRequest(`${ROOMS_API_URL}/api/schedules/${scheduleId}`);
    if (!scheduleResponse.success) {
      return res.status(400).json({ success: false, error: 'Schedule not found' });
    }
    
    // Validar que los asientos están disponibles
    const seatsResponse = await makeRequest(`${ROOMS_API_URL}/api/rooms/${scheduleResponse.data.room_id}/seats`);
    if (!seatsResponse.success) {
      return res.status(400).json({ success: false, error: 'Failed to fetch seats' });
    }
    
    const availableSeats = seatsResponse.data.filter(seat => seat.is_available);
    const requestedSeats = availableSeats.filter(seat => seatIds.includes(seat.id));
    
    if (requestedSeats.length !== seatIds.length) {
      return res.status(400).json({ success: false, error: 'Some seats are not available' });
    }
    
    // Crear la reserva
    const reservationData = {
      userId,
      scheduleId,
      movieId,
      seatIds,
      totalAmount
    };
    
    const reservationResponse = await makeRequest(
      `${RESERVATIONS_API_URL}/api/reservations`,
      'POST',
      reservationData
    );
    
    if (!reservationResponse.success) {
      return res.status(400).json({ success: false, error: 'Failed to create reservation' });
    }
    
    res.status(201).json({
      success: true,
      data: reservationResponse.data,
      message: 'Ticket booked successfully'
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/user-dashboard/:userId - Dashboard del usuario
app.get('/api/user-dashboard/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { limit = 50 } = req.query; // Agregar límite para reservaciones
    
    // Obtener información del usuario
    const userResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/users/${userId}`);
    if (!userResponse.success) {
      return res.status(404).json({ success: false, error: 'User not found' });
    }
    
    // Obtener reservas del usuario con límite
    const reservationsResponse = await makeRequest(`${RESERVATIONS_API_URL}/api/reservations/user/${userId}?limit=${limit}`);
    if (!reservationsResponse.success) {
      return res.status(500).json({ success: false, error: 'Failed to fetch user reservations' });
    }
    
    // Enriquecer reservas con información de películas
    const enrichedReservations = await Promise.all(
      reservationsResponse.data.map(async (reservation) => {
        try {
          // Obtener información de la película
          const movieResponse = await makeRequest(`${MOVIES_API_URL}/api/movies/${reservation.movieId}`);
          const movie = movieResponse.success ? movieResponse.data : null;
          
          // Obtener información del horario y sala
          const scheduleResponse = await makeRequest(`${ROOMS_API_URL}/api/schedules/${reservation.scheduleId}`);
          const schedule = scheduleResponse.success ? scheduleResponse.data : null;
          
          return {
            ...reservation,
            movie,
            schedule
          };
        } catch (error) {
          console.error(`Error enriching reservation ${reservation.id}:`, error.message);
          return reservation;
        }
      })
    );
    
    res.json({
      success: true,
      data: {
        user: userResponse.data,
        reservations: enrichedReservations
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/movie-details/:movieId - Obtener detalles completos de una película
app.get('/api/movie-details/:movieId', async (req, res) => {
  try {
    const { movieId } = req.params;
    
    // Obtener información de la película
    const movieResponse = await makeRequest(`${MOVIES_API_URL}/api/movies/${movieId}`);
    if (!movieResponse.success) {
      return res.status(404).json({ success: false, error: 'Movie not found' });
    }
    
    // Obtener horarios de la película
    const schedulesResponse = await makeRequest(`${ROOMS_API_URL}/api/schedules/movie/${movieId}`);
    const schedules = schedulesResponse.success ? schedulesResponse.data : [];
    
    // Enriquecer horarios con información de salas
    const enrichedSchedules = await Promise.all(
      schedules.map(async (schedule) => {
        try {
          const roomResponse = await makeRequest(`${ROOMS_API_URL}/api/rooms/${schedule.room_id}`);
          const room = roomResponse.success ? roomResponse.data : null;
          
          return {
            ...schedule,
            room
          };
        } catch (error) {
          console.error(`Error enriching schedule ${schedule.id}:`, error.message);
          return schedule;
        }
      })
    );
    
    res.json({
      success: true,
      data: {
        movie: movieResponse.data,
        schedules: enrichedSchedules
      }
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// ===== PROXY ENDPOINTS =====

/**
 * @swagger
 * /api/movies:
 *   get:
 *     summary: Proxy to Movies API
 *     description: Forward all movie-related requests to the Movies microservice
 *     tags: [Movies]
 *     responses:
 *       200:
 *         description: Successful proxy response
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/SuccessResponse'
 *       500:
 *         description: Service error
 *   post:
 *     summary: Proxy to Movies API
 *     description: Forward all movie-related requests to the Movies microservice
 *     tags: [Movies]
 *     responses:
 *       200:
 *         description: Successful proxy response
 *       500:
 *         description: Service error
 */
app.use('/api/movies', async (req, res) => {
  try {
    const url = `${MOVIES_API_URL}/api/movies${req.url}`;
    const response = await makeRequest(url, req.method, req.body);
    res.json(response);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Proxy para Rooms API
app.use('/api/rooms', async (req, res) => {
  try {
    const url = `${ROOMS_API_URL}/api/rooms${req.url}`;
    const response = await makeRequest(url, req.method, req.body);
    res.json(response);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Proxy para Reservations API
app.use('/api/reservations', async (req, res) => {
  try {
    const url = `${RESERVATIONS_API_URL}/api/reservations${req.url}`;
    const response = await makeRequest(url, req.method, req.body);
    res.json(response);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Proxy para Users API
app.use('/api/users', async (req, res) => {
  try {
    const url = `${RESERVATIONS_API_URL}/api/users${req.url}`;
    const response = await makeRequest(url, req.method, req.body);
    res.json(response);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Proxy para Payments API
app.use('/api/payments', async (req, res) => {
  try {
    const url = `${RESERVATIONS_API_URL}/api/payments${req.url}`;
    const response = await makeRequest(url, req.method, req.body);
    res.json(response);
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Gateway error:', error);
  res.status(500).json({ 
    success: false, 
    error: 'Internal server error' 
  });
});

// Root route - redirect to docs
app.get('/', (req, res) => {
  res.redirect('/docs');
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ 
    success: false, 
    error: 'Endpoint not found' 
  });
});

app.listen(PORT, () => {
  console.log(`Gateway API running on port ${PORT}`);
  console.log(`Movies API: ${MOVIES_API_URL}`);
  console.log(`Rooms API: ${ROOMS_API_URL}`);
  console.log(`Reservations API: ${RESERVATIONS_API_URL}`);
});