import { NextResponse } from 'next/server';
import connectDB from '../../../lib/mongodb';
import Movie from '../../../models/Movie';

// GET /api/movies - Listar películas
export async function GET(request) {
  try {
    await connectDB();
    
    const { searchParams } = new URL(request.url);
    const page = parseInt(searchParams.get('page')) || 1;
    const limit = parseInt(searchParams.get('limit')) || 10;
    const genre = searchParams.get('genre');
    const search = searchParams.get('search');
    const featured = searchParams.get('featured');
    
    let query = { isActive: true };
    
    if (genre) {
      query.genre = { $in: [genre] };
    }
    
    if (search) {
      query.$text = { $search: search };
    }
    
    if (featured === 'true') {
      query.rating = { $gte: 7 };
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

// POST /api/movies - Crear película
export async function POST(request) {
  try {
    await connectDB();
    
    const body = await request.json();
    
    const movie = new Movie(body);
    const savedMovie = await movie.save();
    
    return NextResponse.json({
      success: true,
      data: savedMovie
    }, { status: 201 });
  } catch (error) {
    if (error.name === 'ValidationError') {
      return NextResponse.json(
        { success: false, error: 'Validation error', details: error.errors },
        { status: 400 }
      );
    }
    
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}