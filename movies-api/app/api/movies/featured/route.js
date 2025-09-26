import { NextResponse } from 'next/server';
import connectDB from '../../../../lib/mongodb';
import Movie from '../../../../models/Movie';

// GET /api/movies/featured - Obtener películas destacadas
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