const swaggerJsdoc = require('swagger-jsdoc');

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Cinema Analytics API',
      version: '1.0.0',
      description: 'Analytics and Reporting Microservice for Cinema Management System - Data insights and business intelligence',
      contact: {
        name: 'Cinema Analytics Team',
        email: 'analytics@cinema.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:3005',
        description: 'Development server'
      },
      {
        url: 'https://analytics.cinema.com',
        description: 'Production server'
      }
    ],
    tags: [
      {
        name: 'Revenue Analytics',
        description: 'Financial and revenue analysis operations'
      },
      {
        name: 'Movie Analytics',
        description: 'Movie performance and popularity analytics'
      },
      {
        name: 'User Analytics',
        description: 'User behavior and engagement analytics'
      },
      {
        name: 'Room Analytics',
        description: 'Room utilization and occupancy analytics'
      },
      {
        name: 'Booking Analytics',
        description: 'Reservation and booking pattern analytics'
      },
      {
        name: 'Reports',
        description: 'Comprehensive business reports generation'
      },
      {
        name: 'Health',
        description: 'Analytics service health and status'
      }
    ],
    components: {
      schemas: {
        RevenueStats: {
          type: 'object',
          properties: {
            totalRevenue: {
              type: 'number',
              format: 'float',
              description: 'Total revenue amount'
            },
            period: {
              type: 'string',
              description: 'Time period for the revenue calculation'
            },
            currency: {
              type: 'string',
              example: 'USD',
              description: 'Currency code'
            },
            breakdown: {
              type: 'object',
              properties: {
                byMovie: {
                  type: 'object',
                  description: 'Revenue breakdown by movie'
                },
                byRoom: {
                  type: 'object',
                  description: 'Revenue breakdown by room'
                },
                byDate: {
                  type: 'object',
                  description: 'Revenue breakdown by date'
                }
              }
            }
          }
        },
        MovieStats: {
          type: 'object',
          properties: {
            movieId: {
              type: 'string',
              description: 'Movie ID'
            },
            title: {
              type: 'string',
              description: 'Movie title'
            },
            totalBookings: {
              type: 'integer',
              description: 'Total number of bookings'
            },
            totalRevenue: {
              type: 'number',
              format: 'float',
              description: 'Total revenue generated'
            },
            averageRating: {
              type: 'number',
              format: 'float',
              description: 'Average user rating'
            },
            occupancyRate: {
              type: 'number',
              format: 'float',
              description: 'Average occupancy rate percentage'
            },
            popularShowtimes: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Most popular showtime slots'
            }
          }
        },
        UserAnalytics: {
          type: 'object',
          properties: {
            totalUsers: {
              type: 'integer',
              description: 'Total number of users'
            },
            activeUsers: {
              type: 'integer',
              description: 'Number of active users'
            },
            newUsers: {
              type: 'integer',
              description: 'Number of new users in period'
            },
            averageBookingsPerUser: {
              type: 'number',
              format: 'float',
              description: 'Average bookings per user'
            },
            topUsers: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  userId: { type: 'integer' },
                  totalBookings: { type: 'integer' },
                  totalSpent: { type: 'number', format: 'float' }
                }
              },
              description: 'Top users by activity'
            }
          }
        },
        RoomUtilization: {
          type: 'object',
          properties: {
            roomId: {
              type: 'integer',
              description: 'Room ID'
            },
            roomName: {
              type: 'string',
              description: 'Room name'
            },
            utilizationRate: {
              type: 'number',
              format: 'float',
              description: 'Utilization rate percentage'
            },
            totalShows: {
              type: 'integer',
              description: 'Total number of shows'
            },
            averageOccupancy: {
              type: 'number',
              format: 'float',
              description: 'Average occupancy percentage'
            },
            peakHours: {
              type: 'array',
              items: {
                type: 'string'
              },
              description: 'Peak utilization hours'
            }
          }
        },
        BookingTrends: {
          type: 'object',
          properties: {
            period: {
              type: 'string',
              description: 'Analysis period'
            },
            totalBookings: {
              type: 'integer',
              description: 'Total bookings in period'
            },
            bookingsByDay: {
              type: 'object',
              description: 'Daily booking distribution'
            },
            bookingsByHour: {
              type: 'object',
              description: 'Hourly booking distribution'
            },
            averageBookingValue: {
              type: 'number',
              format: 'float',
              description: 'Average booking amount'
            },
            cancellationRate: {
              type: 'number',
              format: 'float',
              description: 'Booking cancellation rate percentage'
            }
          }
        },
        BusinessReport: {
          type: 'object',
          properties: {
            reportId: {
              type: 'string',
              description: 'Unique report identifier'
            },
            generatedAt: {
              type: 'string',
              format: 'date-time',
              description: 'Report generation timestamp'
            },
            period: {
              type: 'object',
              properties: {
                startDate: { type: 'string', format: 'date' },
                endDate: { type: 'string', format: 'date' }
              }
            },
            summary: {
              type: 'object',
              properties: {
                totalRevenue: { type: 'number', format: 'float' },
                totalBookings: { type: 'integer' },
                uniqueCustomers: { type: 'integer' },
                averageTicketPrice: { type: 'number', format: 'float' }
              }
            },
            topMovies: {
              type: 'array',
              items: {
                $ref: '#/components/schemas/MovieStats'
              }
            },
            roomUtilization: {
              type: 'array',
              items: {
                $ref: '#/components/schemas/RoomUtilization'
              }
            }
          }
        },
        AnalyticsResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              example: true
            },
            data: {
              type: 'object',
              description: 'Analytics data payload'
            },
            meta: {
              type: 'object',
              properties: {
                generatedAt: {
                  type: 'string',
                  format: 'date-time'
                },
                period: {
                  type: 'string'
                },
                dataPoints: {
                  type: 'integer'
                }
              }
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
            error: {
              type: 'string',
              description: 'Error message'
            },
            details: {
              type: 'string',
              description: 'Detailed error information'
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