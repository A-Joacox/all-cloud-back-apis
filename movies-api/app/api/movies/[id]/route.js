import { NextResponse } from 'next/server';
import connectDB from '../../../../lib/mongodb';
import Movie from '../../../../models/Movie';

// GET /api/movies/[id] - Obtener película específica
export async function GET(request, { params }) {
  try {
    await connectDB();
    
    const movie = await Movie.findById(params.id);
    
    if (!movie) {
      return NextResponse.json(
        { success: false, error: 'Movie not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({
      success: true,
      data: movie
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

// PUT /api/movies/[id] - Actualizar película
export async function PUT(request, { params }) {
  try {
    await connectDB();
    
    const body = await request.json();
    
    const movie = await Movie.findByIdAndUpdate(
      params.id,
      body,
      { new: true, runValidators: true }
    );
    
    if (!movie) {
      return NextResponse.json(
        { success: false, error: 'Movie not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({
      success: true,
      data: movie
    });
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

// DELETE /api/movies/[id] - Eliminar película (soft delete)
export async function DELETE(request, { params }) {
  try {
    await connectDB();
    
    const movie = await Movie.findByIdAndUpdate(
      params.id,
      { isActive: false },
      { new: true }
    );
    
    if (!movie) {
      return NextResponse.json(
        { success: false, error: 'Movie not found' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({
      success: true,
      message: 'Movie deactivated successfully'
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}