import swaggerJsdoc from 'swagger-jsdoc';

const options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Movies API',
      version: '1.0.0',
      description: 'Cinema Movies Microservice - MongoDB based API for managing movies and genres',
      contact: {
        name: 'Cinema API Team',
        email: 'api@cinema.com'
      },
    },
    servers: [
      {
        url: process.env.NODE_ENV === 'production' ? 'https://api.cinema.com' : 'http://localhost:3001',
        description: process.env.NODE_ENV === 'production' ? 'Production server' : 'Development server',
      },
    ],
    components: {
      schemas: {
        Movie: {
          type: 'object',
          properties: {
            _id: {
              type: 'string',
              description: 'MongoDB ObjectId',
              example: '507f1f77bcf86cd799439011'
            },
            title: {
              type: 'string',
              description: 'Movie title',
              example: 'The Matrix'
            },
            description: {
              type: 'string',
              description: 'Movie description',
              example: 'A computer hacker learns from mysterious rebels about the true nature of his reality.'
            },
            genre: {
              type: 'string',
              description: 'Movie genre',
              example: 'Action'
            },
            duration: {
              type: 'number',
              description: 'Duration in minutes',
              example: 136
            },
            rating: {
              type: 'number',
              minimum: 0,
              maximum: 10,
              description: 'Movie rating',
              example: 8.7
            },
            releaseDate: {
              type: 'string',
              format: 'date',
              description: 'Release date',
              example: '1999-03-31'
            },
            director: {
              type: 'string',
              description: 'Director name',
              example: 'Lana Wachowski, Lilly Wachowski'
            },
            poster: {
              type: 'string',
              description: 'Poster URL',
              example: 'https://example.com/poster.jpg'
            },
            isActive: {
              type: 'boolean',
              description: 'Whether the movie is active',
              example: true
            }
          }
        },
        Genre: {
          type: 'object',
          properties: {
            _id: {
              type: 'string',
              description: 'MongoDB ObjectId',
              example: '507f1f77bcf86cd799439012'
            },
            name: {
              type: 'string',
              description: 'Genre name',
              example: 'Action'
            },
            description: {
              type: 'string',
              description: 'Genre description',
              example: 'Fast-paced movies with exciting sequences'
            },
            isActive: {
              type: 'boolean',
              description: 'Whether the genre is active',
              example: true
            }
          }
        },
        ApiResponse: {
          type: 'object',
          properties: {
            success: {
              type: 'boolean',
              description: 'Whether the request was successful'
            },
            data: {
              type: 'object',
              description: 'Response data'
            },
            message: {
              type: 'string',
              description: 'Response message'
            },
            error: {
              type: 'string',
              description: 'Error message if any'
            }
          }
        }
      }
    },
    tags: [
      {
        name: 'Movies',
        description: 'Movie management operations'
      },
      {
        name: 'Genres',
        description: 'Genre management operations'
      },
      {
        name: 'Health',
        description: 'Health check operations'
      }
    ]
  },
  apis: ['./app/api/**/*.js'], // Paths to files containing OpenAPI definitions
};

const swaggerSpec = swaggerJsdoc(options);

export default swaggerSpec;