import './globals.css'

export const metadata = {
  title: 'Movies API',
  description: 'Cinema Movies Microservice API',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
