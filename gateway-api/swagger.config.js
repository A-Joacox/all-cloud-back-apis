const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Cinema Gateway API',
      version: '1.0.0',
      description: 'API Gateway for Cinema Microservices - Central routing and orchestration layer',
      contact: {
        name: 'Cinema API Team',
        email: 'api@cinema.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:3004',
        description: 'Development server'
      },
      {
        url: 'https://gateway.cinema.com',
        description: 'Production server'
      }
    ],
    tags: [
      {
        name: 'Movies',
        description: 'Movie catalog operations (proxied to Movies API)'
      },
      {
        name: 'Rooms',
        description: 'Cinema room operations (proxied to Rooms API)'
      },
      {
        name: 'Reservations',
        description: 'Reservation operations (proxied to Reservations API)'
      },
      {
        name: 'Health',
        description: 'Gateway health and status operations'
      },
      {
        name: 'System',
        description: 'System-wide operations and orchestration'
      }
    ],
    components: {
      schemas: {
        Movie: {
          type: 'object',
          properties: {
            _id: {
              type: 'string',
              description: 'MongoDB Object ID'
            },
            title: {
              type: 'string',
              description: 'Movie title'
            },
            description: {
              type: 'string',
              description: 'Movie description'
            },
            releaseDate: {
              type: 'string',
              format: 'date',
              description: 'Release date'
            },
            duration: {
              type: 'integer',
              description: 'Duration in minutes'
            },
            genre: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Movie genres'
            },
            rating: {
              type: 'number',
              format: 'float',
              description: 'Movie rating (0-10)'
            },
            posterUrl: {
              type: 'string',
              description: 'Poster image URL'
            }
          }
        },
        Room: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              description: 'Room ID'
            },
            name: {
              type: 'string',
              description: 'Room name'
            },
            capacity: {
              type: 'integer',
              description: 'Room capacity'
            },
            type: {
              type: 'string',
              enum: ['IMAX', 'VIP', 'Standard', '4DX'],
              description: 'Room type'
            },
            features: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Room features'
            }
          }
        },
        Reservation: {
          type: 'object',
          properties: {
            id: {
              type: 'integer',
              description: 'Reservation ID'
            },
            userId: {
              type: 'integer',
              description: 'User ID'
            },
            movieId: {
              type: 'string',
              description: 'Movie ID (MongoDB ObjectId)'
            },
            roomId: {
              type: 'integer',
              description: 'Room ID'
            },
            showtime: {
              type: 'string',
              format: 'date-time',
              description: 'Show datetime'
            },
            seats: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Reserved seat numbers'
            },
            status: {
              type: 'string',
              enum: ['CONFIRMED', 'CANCELLED', 'PENDING'],
              description: 'Reservation status'
            },
            totalAmount: {
              type: 'number',
              format: 'float',
              description: 'Total reservation amount'
            }
          }
        },
        ErrorResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: false
            },
            message: {
              type: 'string',
              description: 'Error message'
            },
            error: {
              type: 'string',
              description: 'Detailed error information'
            }
          }
        },
        SuccessResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: true
            },
            data: {
              type: 'object',
              description: 'Response data'
            },
            message: {
              type: 'string',
              description: 'Success message'
            }
          }
        },
        HealthStatus: {
          type: 'object',
          properties: {
            status: {
              type: 'string',
              enum: ['healthy', 'unhealthy'],
              description: 'Gateway health status'
            },
            timestamp: {
              type: 'string',
              format: 'date-time',
              description: 'Health check timestamp'
            },
            services: {
              type: 'object',
              properties: {
                movies: {
                  type: 'object',
                  properties: {
                    status: { type: 'string' },
                    url: { type: 'string' },
                    responseTime: { type: 'number' }
                  }
                },
                rooms: {
                  type: 'object',
                  properties: {
                    status: { type: 'string' },
                    url: { type: 'string' },
                    responseTime: { type: 'number' }
                  }
                },
                reservations: {
                  type: 'object',
                  properties: {
                    status: { type: 'string' },
                    url: { type: 'string' },
                    responseTime: { type: 'number' }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  apis: ['./server.js'], // Path to the API docs
};

const specs = swaggerJsdoc(options);
module.exports = specs;