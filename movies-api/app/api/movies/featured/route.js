import { NextResponse } from 'next/server';
import connectDB from '../../../../lib/mongodb';
import Movie from '../../../../models/Movie';

/**
 * @swagger
 * /api/movies/featured:
 *   get:
 *     tags: [Movies]
 *     summary: Get featured movies
 *     description: Retrieve a list of featured movies (high rating, sorted by rating and release date)
 *     parameters:
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 5
 *         description: Number of featured movies to return
 *     responses:
 *       200:
 *         description: Featured movies retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/ApiResponse'
 *       500:
 *         description: Internal server error
 */
export async function GET(request) {
  try {
    await connectDB();
    
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit')) || 5;
    
    const movies = await Movie.find({
      isActive: true,
      rating: { $gte: 7 }
    })
    .sort({ rating: -1, releaseDate: -1 })
    .limit(limit)
    .lean();
    
    return NextResponse.json({
      success: true,
      data: movies
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}