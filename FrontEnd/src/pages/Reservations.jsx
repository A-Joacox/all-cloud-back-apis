import { useState, useEffect } from 'react'
import { reservationsApi, gatewayApi } from '../services/api'
import './Reservations.css'

const Reservations = () => {
  const [reservations, setReservations] = useState([])
  const [loading, setLoading] = useState(false) // Changed from true to false
  const [error, setError] = useState(null)
  const [userId, setUserId] = useState('1') // Default for demo
  const [elapsed, setElapsed] = useState(0)

  // Removed automatic loading on mount - user must click button

  const fetchReservations = async () => {
    try {
      setLoading(true)
      setError(null)
      setElapsed(0)

      console.log('Attempting to fetch reservations for user:', userId)

      const start = Date.now()
      const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000)

      const apiCall = async () => {
        try {
          console.log('Trying gateway API user dashboard...')
          const gatewayResponse = await gatewayApi.getUserDashboard(userId)
          const reservationsData = gatewayResponse.data?.data?.reservations || gatewayResponse.data?.reservations || []
          return reservationsData
        } catch (gatewayError) {
          console.log('Gateway API failed, trying reservations API...', gatewayError.message)
          try {
            console.log('Trying to get all reservations...')
            const allReservationsResponse = await reservationsApi.getReservations()
            const allReservations = allReservationsResponse.data || []
            const userReservations = Array.isArray(allReservations) ? allReservations.filter(r => r.userId == userId || r.user?.id == userId) : []
            return userReservations
          } catch (generalError) {
            console.log('General reservations endpoint failed, trying user-specific...', generalError.message)
            const response = await reservationsApi.getUserReservations(userId)
            return response.data || []
          }
        }
      }

      const reservationsData = await apiCall()
      setReservations(reservationsData)
      clearInterval(timer)
      setElapsed(Math.floor((Date.now() - start) / 1000))
    } catch (err) {
      console.error('Error fetching reservations:', err)
      console.error('Error details:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        url: err.config?.url,
        message: err.message
      })

      if (err.response?.status === 404) {
        setError('👤 User not found - Please check the user ID and try again.')
      } else if (err.response?.status === 500) {
        setError(`🔧 Server error (500): The reservations service is experiencing internal issues. ${err.response?.data?.error || 'Please try again later.'}`)
      } else {
        setError(`❌ Service unavailable: The reservations service returned an error. ${err.message}`)
      }
      setReservations([])
      setElapsed(0)
    } finally {
      setLoading(false)
    }
  }

  const handleUserIdChange = (e) => {
    setUserId(e.target.value)
  }

  const testUsersEndpoint = async () => {
    try {
      console.log('Testing users endpoint...')
      setLoading(true)
      setElapsed(0)
      const start = Date.now()
      const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 1000)

      const usersResponse = await reservationsApi.getUsers()
      clearInterval(timer)
      setElapsed(Math.floor((Date.now() - start) / 1000))
      console.log('Users response:', usersResponse)
      alert('Users API working! Check console for details.')
    } catch (err) {
      console.error('Users endpoint error:', err)
      alert(`Users API error: ${err.response?.status || 'Unknown'} - ${err.response?.data?.error || err.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div className="loading">Loading reservations... {elapsed > 0 && `(${elapsed}s elapsed)`}</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="reservations">
      <div className="container">
        <h1>My Reservations</h1>

        <div className="user-selector">
          <label>
            User ID:
            <input
              type="text"
              value={userId}
              onChange={handleUserIdChange}
              placeholder="Enter your user ID"
            />
          </label>
          <button onClick={fetchReservations} className="btn-primary">
            Load Reservations
          </button>
        </div>

        {reservations.length > 0 ? (
          <div className="reservations-list">
            {reservations.map(reservation => (
              <div key={reservation.id} className="reservation-card">
                <div className="reservation-header">
                  <h3>Reservation #{reservation.id}</h3>
                  <span className={`status ${reservation.status?.toLowerCase()}`}>
                    {reservation.status || 'CONFIRMED'}
                  </span>
                </div>

                <div className="reservation-details">
                  <p><strong>Movie:</strong> {reservation.movie?.title || 'N/A'}</p>
                  <p><strong>Showtime:</strong> {reservation.schedule ? new Date(reservation.schedule.showtime).toLocaleString() : 'N/A'}</p>
                  <p><strong>Room:</strong> {reservation.schedule?.room?.name || 'N/A'}</p>
                  <p><strong>Seats:</strong> {reservation.seatIds?.join(', ') || 'N/A'}</p>
                  <p><strong>Total Amount:</strong> ${reservation.totalAmount}</p>
                  <p><strong>Booked on:</strong> {new Date(reservation.createdAt).toLocaleDateString()}</p>
                </div>
              </div>
            ))}
          </div>
  ) : null}
      </div>
    </div>
  )
}

export default Reservations
