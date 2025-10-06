# Cinema Booking Frontend

A modern React frontend for the Cinema microservices system.

## Features

- Browse movies with search and filtering
- View detailed movie information
- Book movie tickets with seat selection
- View user reservations

## Tech Stack

- React 19
- React Router
- Axios for API calls
- Modern CSS with responsive design

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:5173](http://localhost:5173) in your browser.

## API Integration

This frontend connects to the following microservices:
- Movies API (port 3001)
- Rooms API (port 3002)
- Reservations API (port 3003)
- Gateway API (port 3004)

All running on http://3.86.188.48
