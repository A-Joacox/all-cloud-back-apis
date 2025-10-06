import axios from 'axios'

// Create axios instance with CORS headers
const apiClient = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to handle CORS
apiClient.interceptors.request.use(
  (config) => {
    // Add any additional headers if needed
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    if (error.response) {
      // Server responded with error status
      console.error('Response data:', error.response.data)
      console.error('Response status:', error.response.status)
    } else if (error.request) {
      // Request was made but no response received
      console.error('No response received:', error.request)
    } else {
      // Something else happened
      console.error('Request setup error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Movies API
export const moviesApi = {
  getMovies: (params = {}) => apiClient.get('/api/movies', { params }),
  getMovie: (id) => apiClient.get(`/api/movies/${id}`),
  getFeaturedMovies: () => apiClient.get('/api/movies/featured'),
  searchMovies: (params) => apiClient.get('/api/movies/search', { params }),
  getGenres: () => apiClient.get('/api/genres')
}

// Gateway API
export const gatewayApi = {
  getShowtimes: (params = {}) => apiClient.get('/api/showtimes', { params }),
  bookTicket: (data) => apiClient.post('/api/book-ticket', data),
  getUserDashboard: (userId) => apiClient.get(`/api/user-dashboard/${userId}`),
  getMovieDetails: (movieId) => apiClient.get(`/api/movie-details/${movieId}`)
}

// Rooms API
export const roomsApi = {
  getRooms: () => apiClient.get('/api/rooms'),
  getRoom: (id) => apiClient.get(`/api/rooms/${id}`),
  getSchedules: (params = {}) => apiClient.get('/api/schedules', { params }),
  // Backend does not provide GET /api/schedules/:id in rooms-api
  // Normalize behavior for the frontend: fetch schedules list and return the matching schedule
  getSchedule: async (id) => {
    const resp = await apiClient.get('/api/schedules')
    // schedules may be in resp.data.data or resp.data
    const raw = resp.data && (resp.data.data || resp.data) || []
    const schedules = Array.isArray(raw) ? raw : [raw]
    const schedule = schedules.find(s => String(s.id) === String(id)) || null
    // Return shape so components can access response.data.data
    return { data: { success: !!schedule, data: schedule } }
  },
  getRoomSeats: (roomId) => apiClient.get(`/api/rooms/${roomId}/seats`)
}

// Reservations API
export const reservationsApi = {
  getReservations: () => apiClient.get('/api/reservations'),
  getUserReservations: (userId) => apiClient.get(`/api/reservations/user/${userId}`),
  createReservation: (data) => apiClient.post('/api/reservations', data),
  getUsers: () => apiClient.get('/api/users'),
  getUser: (id) => apiClient.get(`/api/users/${id}`)
}

// Payments API
export const paymentsApi = {
  processPayment: (data) => apiClient.post('/api/payments', data)
}
