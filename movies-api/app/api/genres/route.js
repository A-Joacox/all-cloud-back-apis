import { NextResponse } from 'next/server';
import connectDB from '../../../lib/mongodb';
import Genre from '../../../models/Genre';

// GET /api/genres - Listar géneros
export async function GET() {
  try {
    await connectDB();
    
    const genres = await Genre.find().sort({ name: 1 });
    
    return NextResponse.json({
      success: true,
      data: genres
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// POST /api/genres - Crear género
export async function POST(request) {
  try {
    await connectDB();
    
    const body = await request.json();
    
    const genre = new Genre(body);
    const savedGenre = await genre.save();
    
    return NextResponse.json({
      success: true,
      data: savedGenre
    }, { status: 201 });
  } catch (error) {
    if (error.code === 11000) {
      return NextResponse.json(
        { success: false, error: 'Genre already exists' },
        { status: 400 }
      );
    }
    
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