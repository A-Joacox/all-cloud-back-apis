import { NextResponse } from 'next/server';
import swaggerSpec from '../../../swagger.config.js';

/**
 * @swagger
 * /api/docs:
 *   get:
 *     tags: [Documentation]
 *     summary: Get OpenAPI specification
 *     description: Returns the OpenAPI specification JSON for the Movies API
 *     responses:
 *       200:
 *         description: OpenAPI specification
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 */
export async function GET() {
  try {
    return NextResponse.json(swaggerSpec);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to generate API documentation' },
      { status: 500 }
    );
  }
}