const { MongoClient } = require('mongodb');
const faker = require('faker');

// Configuración de conexión
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/cinema_movies';
const DATABASE_NAME = 'cinema_movies';

// Datos de ejemplo para géneros
const GENRES = [
    'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary',
    'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller', 'War', 'Western'
];

// Datos de ejemplo para directores
const DIRECTORS = [
    'Christopher Nolan', 'Steven Spielberg', 'Martin Scorsese', 'Quentin Tarantino',
    'Stanley Kubrick', 'Alfred Hitchcock', 'Francis Ford Coppola', 'Ridley Scott',
    'James Cameron', 'Peter Jackson', 'David Fincher', 'Tim Burton',
    'Wes Anderson', 'Coen Brothers', 'Denis Villeneuve', 'Damien Chazelle',
    'Jordan Peele', 'Greta Gerwig', 'Ari Aster', 'Robert Eggers'
];

// Datos de ejemplo para actores
const ACTORS = [
    'Leonardo DiCaprio', 'Tom Hanks', 'Meryl Streep', 'Robert De Niro',
    'Al Pacino', 'Denzel Washington', 'Morgan Freeman', 'Samuel L. Jackson',
    'Brad Pitt', 'Johnny Depp', 'Will Smith', 'Tom Cruise',
    'Scarlett Johansson', 'Emma Stone', 'Jennifer Lawrence', 'Natalie Portman',
    'Ryan Gosling', 'Joaquin Phoenix', 'Christian Bale', 'Matthew McConaughey',
    'Amy Adams', 'Cate Blanchett', 'Sandra Bullock', 'Julia Roberts'
];

// Función para generar una película
function generateMovie() {
    const title = faker.lorem.words(faker.random.number({ min: 1, max: 4 }));
    const genres = faker.random.arrayElements(GENRES, faker.random.number({ min: 1, max: 3 }));
    const director = faker.random.arrayElement(DIRECTORS);
    const cast = faker.random.arrayElements(ACTORS, faker.random.number({ min: 3, max: 8 }));
    
    return {
        title: title.charAt(0).toUpperCase() + title.slice(1),
        description: faker.lorem.paragraphs(faker.random.number({ min: 2, max: 4 })),
        duration: faker.random.number({ min: 60, max: 200 }),
        genre: genres,
        director: director,
        cast: cast,
        releaseDate: faker.date.between('1990-01-01', '2024-12-31'),
        rating: parseFloat(faker.random.number({ min: 0, max: 100 }) / 10).toFixed(1),
        posterUrl: `https://example.com/posters/${faker.random.alphaNumeric(10)}.jpg`,
        trailerUrl: `https://example.com/trailers/${faker.random.alphaNumeric(10)}.mp4`,
        isActive: faker.random.boolean(),
        createdAt: faker.date.between('2020-01-01', new Date()),
        updatedAt: faker.date.between('2020-01-01', new Date())
    };
}

// Función para generar un género
function generateGenre() {
    const name = faker.random.arrayElement(GENRES);
    return {
        name: name,
        description: faker.lorem.sentence(),
        createdAt: faker.date.between('2020-01-01', new Date()),
        updatedAt: faker.date.between('2020-01-01', new Date())
    };
}

async function generateData() {
    const client = new MongoClient(MONGODB_URI);
    
    try {
        await client.connect();
        console.log('Conectado a MongoDB');
        
        const db = client.db(DATABASE_NAME);
        
        // Generar géneros únicos
        console.log('Generando géneros...');
        const genres = [];
        const uniqueGenres = new Set();
        
        for (let i = 0; i < 22; i++) {
            let genre;
            do {
                genre = generateGenre();
            } while (uniqueGenres.has(genre.name));
            
            uniqueGenres.add(genre.name);
            genres.push(genre);
        }
        
        await db.collection('genres').insertMany(genres);
        console.log(`✅ Insertados ${genres.length} géneros`);
        
        // Generar películas
        console.log('Generando películas...');
        const movies = [];
        const MOVIES_COUNT = 8000; // 8,000 películas
        
        for (let i = 0; i < MOVIES_COUNT; i++) {
            movies.push(generateMovie());
            
            // Insertar en lotes de 1000
            if (movies.length === 1000) {
                await db.collection('movies').insertMany(movies);
                console.log(`✅ Insertadas ${movies.length} películas (lote ${Math.floor(i/1000) + 1})`);
                movies.length = 0; // Limpiar array
            }
        }
        
        // Insertar películas restantes
        if (movies.length > 0) {
            await db.collection('movies').insertMany(movies);
            console.log(`✅ Insertadas ${movies.length} películas restantes`);
        }
        
        console.log(`🎬 Total de películas generadas: ${MOVIES_COUNT}`);
        console.log(`🎭 Total de géneros generados: ${genres.length}`);
        
    } catch (error) {
        console.error('Error generando datos:', error);
    } finally {
        await client.close();
        console.log('Conexión cerrada');
    }
}

// Ejecutar si se llama directamente
if (require.main === module) {
    generateData();
}

module.exports = { generateData };