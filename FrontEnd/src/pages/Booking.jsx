import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { roomsApi, gatewayApi } from '../services/api'
import SeatSelector from '../components/SeatSelector'
import './Booking.css'

const Booking = () => {
  const { scheduleId } = useParams()
  const navigate = useNavigate()
  const [schedule, setSchedule] = useState(null)
  const [room, setRoom] = useState(null)
  const [seats, setSeats] = useState([])
  const [selectedSeats, setSelectedSeats] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [bookingData, setBookingData] = useState({
    userId: '', // In a real app, this would come from auth
    totalAmount: 0
  })

  useEffect(() => {
    fetchScheduleDetails()
  }, [scheduleId])

  const fetchScheduleDetails = async () => {
    try {
      setLoading(true)

      // Get schedule details (tolerate different response shapes)
      const scheduleResponse = await roomsApi.getSchedule(scheduleId)
      const scheduleData = scheduleResponse?.data?.data || scheduleResponse?.data || scheduleResponse
      setSchedule(scheduleData)

      if (scheduleData) {
        // Get room details
        const roomResponse = await roomsApi.getRoom(scheduleData.room_id || scheduleData.room_id || scheduleData.roomId)
        const roomData = roomResponse?.data?.data || roomResponse?.data || roomResponse
        setRoom(roomData)

        // Get seats
        const seatsResponse = await roomsApi.getRoomSeats(scheduleData.room_id || scheduleData.room_id || scheduleData.roomId)
        const seatsData = seatsResponse?.data?.data || seatsResponse?.data || seatsResponse
        setSeats(seatsData)
      }

      // Calculate total amount (assuming $10 per seat)
      setBookingData(prev => ({
        ...prev,
        totalAmount: selectedSeats.length * 10
      }))

    } catch (err) {
      setError('Failed to load booking details')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSeatSelect = (seatId) => {
    setSelectedSeats(prev => {
      const newSelected = prev.includes(seatId)
        ? prev.filter(id => id !== seatId)
        : [...prev, seatId]

      setBookingData(prevData => ({
        ...prevData,
        totalAmount: newSelected.length * 10
      }))

      return newSelected
    })
  }

  const handleBooking = async () => {
    if (selectedSeats.length === 0) {
      alert('Please select at least one seat')
      return
    }

    if (!bookingData.userId) {
      // For demo purposes, use a default user ID
      setBookingData(prev => ({ ...prev, userId: '1' }))
      return
    }

    try {
      const bookingPayload = {
        userId: bookingData.userId,
        scheduleId: parseInt(scheduleId),
        movieId: schedule.movie_id,
        seatIds: selectedSeats,
        totalAmount: bookingData.totalAmount
      }

      const response = await gatewayApi.bookTicket(bookingPayload)

      if (response.data.success) {
        alert('Booking successful!')
        navigate('/reservations')
      } else {
        alert('Booking failed: ' + response.data.error)
      }
    } catch (err) {
      console.error('Booking error:', err)
      alert('Booking failed. Please try again.')
    }
  }

  if (loading) return <div className="loading">Loading booking details...</div>
  if (error) return <div className="error">{error}</div>

  return (
    <div className="booking">
      <div className="container">
        <h1>Book Tickets</h1>

        {schedule && room && (
          <div className="booking-info">
            <div className="showtime-info">
              <h2>{room.name}</h2>
              <p>Screen Type: {room.screen_type}</p>
              <p>Showtime: {new Date(schedule.showtime).toLocaleString()}</p>
              <p>Price per seat: $10</p>
            </div>

            <div className="seat-selection">
              <h3>Select Your Seats</h3>
              <SeatSelector
                seats={seats}
                selectedSeats={selectedSeats}
                onSeatSelect={handleSeatSelect}
              />
            </div>

            <div className="booking-summary">
              <h3>Booking Summary</h3>
              <p>Selected Seats: {selectedSeats.length}</p>
              <p>Total Amount: ${bookingData.totalAmount}</p>

              <div className="user-input">
                <label>
                  User ID (for demo):
                  <input
                    type="text"
                    value={bookingData.userId}
                    onChange={(e) => setBookingData(prev => ({ ...prev, userId: e.target.value }))}
                    placeholder="Enter user ID"
                  />
                </label>
              </div>

              <button
                onClick={handleBooking}
                className="btn-primary"
                disabled={selectedSeats.length === 0}
              >
                Confirm Booking
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Booking
