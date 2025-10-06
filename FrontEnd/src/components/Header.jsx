import { Link } from 'react-router-dom'
import './Header.css'

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <Link to="/" className="logo">
          <h1>Cinema Booking</h1>
        </Link>
        <nav>
          <Link to="/">Movies</Link>
          <Link to="/reservations">My Reservations</Link>
        </nav>
      </div>
    </header>
  )
}

export default Header
