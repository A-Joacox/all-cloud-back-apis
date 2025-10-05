/** @type {import('next').NextConfig} */
const nextConfig = {
  // Removed deprecated appDir and api config
  output: 'standalone',
  eslint: {
    ignoreDuringBuilds: true,
  },
}

module.exports = nextConfig