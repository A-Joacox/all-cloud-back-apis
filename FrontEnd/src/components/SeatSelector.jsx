import './SeatSelector.css'

const SeatSelector = ({ seats, selectedSeats, onSeatSelect }) => {
  // Group seats by row (assuming seat IDs are like 'A1', 'A2', etc.)
  const groupedSeats = seats.reduce((acc, seat) => {
    const row = seat.id.charAt(0)
    if (!acc[row]) acc[row] = []
    acc[row].push(seat)
    return acc
  }, {})

  return (
    <div className="seat-selector">
      <div className="screen">SCREEN</div>
      <div className="seats-grid">
        {Object.entries(groupedSeats).map(([row, rowSeats]) => (
          <div key={row} className="seat-row">
            <span className="row-label">{row}</span>
            <div className="seats">
              {rowSeats.map(seat => (
                <button
                  key={seat.id}
                  className={`seat ${seat.is_available ? 'available' : 'occupied'} ${
                    selectedSeats.includes(seat.id) ? 'selected' : ''
                  }`}
                  onClick={() => seat.is_available && onSeatSelect(seat.id)}
                  disabled={!seat.is_available}
                >
                  {seat.id.slice(1)}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      <div className="legend">
        <div className="legend-item">
          <div className="seat available"></div>
          <span>Available</span>
        </div>
        <div className="legend-item">
          <div className="seat selected"></div>
          <span>Selected</span>
        </div>
        <div className="legend-item">
          <div className="seat occupied"></div>
          <span>Occupied</span>
        </div>
      </div>
    </div>
  )
}

export default SeatSelector
