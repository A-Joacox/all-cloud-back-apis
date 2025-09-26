import { NextResponse } from 'next/server';
import connectDB from '../../../../lib/mongodb';
import Movie from '../../../../models/Movie';

// GET /api/movies/search - Buscar películas
export async function GET(request) {
  try {
    await connectDB();
    
    const { searchParams } = new URL(request.url);
    const genre = searchParams.get('genre');
    const search = searchParams.get('q');
    const page = parseInt(searchParams.get('page')) || 1;
    const limit = parseInt(searchParams.get('limit')) || 10;
    
    let query = { isActive: true };
    
    if (genre) {
      query.genre = { $in: [genre] };
    }
    
    if (search) {
      query.$text = { $search: search };
    }
    
    const skip = (page - 1) * limit;
    
    const movies = await Movie.find(query)
      .sort({ releaseDate: -1 })
      .skip(skip)
      .limit(limit)
      .lean();
    
    const total = await Movie.countDocuments(query);
    
    return NextResponse.json({
      success: true,
      data: movies,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}