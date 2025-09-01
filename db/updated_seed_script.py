# db/seed_script.py
"""
Script de seed completo para Cinema Tickets API
Incluye usuarios, películas, teatros, horarios y fechas dinámicas inteligentes
"""

import sys
import os
from datetime import date, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.models import User, Movie, UserRole
from app.models.theater import Theater, TheaterMovie, MovieShowtime, ShowtimeFormat
from app.models.movie import MovieStatus
from app.models.base import Base


def create_seed_data():
    """Crear datos de seed completos con fechas dinámicas"""
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existen datos
        if db.query(User).count() > 0:
            print("🔄 Datos ya existen. Actualizando fechas y horarios...")
            update_dates_and_showtimes(db)
            return
        
        print("🎬 CINEMA TICKETS - CREANDO SEED DATA")
        print("=" * 50)
        
        # 1. CREAR USUARIOS
        print("\n👥 Creando usuarios...")
        
        admin_user = User(
            email="admin@cinema.com",
            phone="3501234567",
            first_name="Admin",
            last_name="Cinema",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )

        customers = [
            User(
                email="juan.perez@gmail.com",
                phone="3201234567",
                first_name="Juan",
                last_name="Pérez",
                password_hash=get_password_hash("customer123"),
                role=UserRole.CUSTOMER,
                is_active=True
            ),
            User(
                email="maria.rodriguez@gmail.com",
                phone="3151234567",
                first_name="María",
                last_name="Rodríguez",
                password_hash=get_password_hash("customer123"),
                role=UserRole.CUSTOMER,
                is_active=True
            ),
            User(
                email="carlos.martinez@hotmail.com",
                phone="3121234567",
                first_name="Carlos",
                last_name="Martínez",
                password_hash=get_password_hash("customer123"),
                role=UserRole.CUSTOMER,
                is_active=True
            )
        ]

        all_users = [admin_user] + customers
        db.add_all(all_users)
        db.commit()
        print(f"✅ {len(all_users)} usuarios creados")

        # 2. CREAR TEATROS (funcionalidad adicional)
        print("\n🏢 Creando teatros...")
        
        theaters_data = [
            {
                "name": "Chipichape",
                "location": "Centro Comercial Chipichape, Cali",
                "description": "Complejo de cines premium con tecnología de última generación"
            },
            {
                "name": "Cosmocentro", 
                "location": "Centro Comercial Cosmocentro, Cali",
                "description": "Salas de cine familiares en el corazón de la ciudad"
            },
            {
                "name": "Palmetto",
                "location": "Centro Comercial Palmetto, Cali", 
                "description": "Experiencia cinematográfica de lujo con salas VIP"
            },
            {
                "name": "Río Cauca",
                "location": "Centro Comercial Río Cauca, Cali",
                "description": "Cines modernos con excelente ubicación"
            },
            {
                "name": "Unicali",
                "location": "Universidad del Valle, Cali",
                "description": "Salas de cine universitarias con precios especiales"
            }
        ]
        
        theaters = [Theater(**theater_data) for theater_data in theaters_data]
        db.add_all(theaters)
        db.commit()
        print(f"✅ {len(theaters)} teatros creados")

        # 3. CREAR PELÍCULAS CON FECHAS INTELIGENTES
        print("\n🎭 Creando películas con fechas dinámicas...")
        
        # Fechas base inteligentes
        today = date.today()
        
        movies_data = [
            # PELÍCULAS EN CARTELERA (estrenadas recientemente)
            {
                "title": "Un Poeta",
                "description": "La obsesión de Óscar Restrepo por la poesía no le trajo ninguna gloria. Envejecido y errático, ha sucumbido al cliché del poeta en la penumbra. Conocer a Yurlady, una humilde adolescente, y ayudarle a cultivar su talento trae algo de luz a sus días, pero arrastrarla al mundo de los poetas tal vez no sea el camino.",
                "genre": "Comedia Dramática",
                "duration": 120,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Iván D. Gaona", 
                "country": "Colombia",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=10),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            {
                "title": "El Conjuro 4: Últimos Ritos",
                "description": "Cuando los investigadores paranormales Ed y Lorraine Warren se ven envueltos en otro aterrador caso relacionado con misteriosas criaturas, se ven obligados a resolverlo todo por última vez.",
                "genre": "Terror",
                "duration": 131,
                "rating": "R",
                "price": 20000.0,
                "director": "Michael Chaves",
                "country": "Estados Unidos", 
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=5),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/3/0/3/0/80303-2-esl-CO/7381965b1505-warner_theconjuring_cinecol_480x670.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/8/0/3/0/80308-2-esl-CO/812a7d6b4522-warner_theconjuring_cinecol_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/6/0/3/0/80306-2-esl-CO/3cbafc21ce34-warner_theconjuring_cinecol_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/7/0/3/0/80307-2-esl-CO/d840c3f43af0-warner_theconjuring_cinecol_510x510.jpg"
            },
            {
                "title": "Spider-Man: No Way Home",
                "description": "Peter Parker busca la ayuda del Doctor Strange para hacer que el mundo olvide que él es Spider-Man. Sin embargo, el hechizo sale mal y villanos peligrosos de otros universos comienzan a aparecer.",
                "genre": "Acción",
                "duration": 148,
                "rating": "PG-13",
                "price": 22000.0,
                "director": "Jon Watts",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            {
                "title": "Black Panther: Wakanda Forever",
                "description": "La reina Ramonda, Shuri, M'Baku, Okoye y las Dora Milaje luchan para proteger su nación tras la muerte del rey T'Challa. Los wakandanos se esfuerzan por abrazar su próximo capítulo.",
                "genre": "Acción",
                "duration": 161,
                "rating": "PG-13",
                "price": 17000.0,
                "director": "Ryan Coogler",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=7),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            
            # PRÓXIMOS ESTRENOS
            {
                "title": "Avatar: El Camino del Agua",
                "description": "Jake y Neytiri exploran nuevos territorios acuáticos de Pandora en esta secuela épica.",
                "genre": "Ciencia Ficción",
                "duration": 192,
                "rating": "PG-13", 
                "price": 25000.0,
                "director": "James Cameron",
                "country": "Estados Unidos",
                "status": MovieStatus.COMING_SOON,
                "is_presale": False,
                "release_date": today + timedelta(days=14),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            
            # PREVENTAS (funcionalidad adicional)
            {
                "title": "Dune: Parte Dos", 
                "description": "Paul Atreides continúa su épico viaje en el peligroso planeta Arrakis.",
                "genre": "Ciencia Ficción",
                "duration": 166,
                "rating": "PG-13",
                "price": 27000.0,
                "director": "Denis Villeneuve",
                "country": "Estados Unidos",
                "status": MovieStatus.COMING_SOON,
                "is_presale": True,
                "release_date": today + timedelta(days=45),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            {
                "title": "The Batman 2",
                "description": "Batman continúa su lucha contra el crimen en Gotham enfrentando nuevos enemigos.",
                "genre": "Acción",
                "duration": 170,
                "rating": "PG-13",
                "price": 24000.0,
                "director": "Matt Reeves",
                "country": "Estados Unidos", 
                "status": MovieStatus.COMING_SOON,
                "is_presale": True,
                "release_date": today + timedelta(days=52),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            
            # PELÍCULAS ADICIONALES PARA DIVERSIDAD
            {
                "title": "Encanto",
                "description": "Una niña extraordinaria de una familia mágica que vive en una casa mágica en las montañas de Colombia, lucha por demostrar que ella también es especial.",
                "genre": "Animación",
                "duration": 102,
                "rating": "PG",
                "price": 14000.0,
                "director": "Jared Bush",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=14),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            },
            {
                "title": "Minions: The Rise of Gru",
                "description": "En los años 70, Gru crece en los suburbios, siendo un gran fan de un grupo de supervillanos conocidos como los Vicious 6.",
                "genre": "Animación",
                "duration": 87,
                "rating": "PG", 
                "price": 13000.0,
                "director": "Kyle Balda",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=21),
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
            }
        ]
        
        movies = []
        for movie_data in movies_data:
            movie = Movie(
                **movie_data,
                max_capacity=100,
                available_tickets=100,
                is_active=True
            )
            movies.append(movie)
        
        db.add_all(movies)
        db.commit()
        print(f"✅ {len(movies)} películas creadas con fechas inteligentes")
        
        # 4. ASIGNAR PELÍCULAS A TEATROS
        print("\n🔗 Asignando películas a teatros...")
        theater_movies = []
        
        for movie in movies:
            for theater in theaters:
                theater_movie = TheaterMovie(
                    theater_id=theater.id,
                    movie_id=movie.id,
                    capacity=100,
                    available_tickets=100
                )
                theater_movies.append(theater_movie)
        
        db.add_all(theater_movies)
        db.commit()
        print(f"✅ {len(theater_movies)} asignaciones teatro-película creadas")
        
        # 5. CREAR HORARIOS INTELIGENTES (funcionalidad adicional)
        print("\n⏰ Creando horarios inteligentes...")
        create_intelligent_showtimes(db, movies, theaters, today)
        
        # 6. ESTADÍSTICAS FINALES
        showtimes_count = db.query(MovieShowtime).count()
        
        print(f"\n📊 RESUMEN DE SEED DATA CREADO:")
        print("=" * 50)
        print(f"👥 Usuarios: {len(all_users)} (1 admin, {len(customers)} clientes)")
        print(f"🏢 Teatros: {len(theaters)}")
        print(f"🎭 Películas: {len(movies)}")
        print(f"   - En cartelera: {len([m for m in movies if m.status == MovieStatus.IN_THEATERS])}")
        print(f"   - Próximos estrenos: {len([m for m in movies if m.status == MovieStatus.COMING_SOON and not m.is_presale])}")
        print(f"   - En preventa: {len([m for m in movies if m.is_presale])}")
        print(f"🔗 Asignaciones teatro-película: {len(theater_movies)}")
        print(f"⏰ Horarios programados: {showtimes_count}")
        
        print(f"\n📅 CONFIGURACIÓN DE FECHAS:")
        print(f"   - Hoy: {today.strftime('%d-%b-%Y')}")
        print(f"   - Horarios desde: {today.strftime('%d-%b-%Y')}")
        print(f"   - Horarios hasta: {(today + timedelta(days=14)).strftime('%d-%b-%Y')}")
        
        print(f"\n🔐 CREDENCIALES DE ACCESO:")
        print("   - Admin: admin@cinema.com / admin123")
        print("   - Cliente 1: juan.perez@gmail.com / customer123")
        print("   - Cliente 2: maria.rodriguez@gmail.com / customer123")
        print("   - Cliente 3: carlos.martinez@hotmail.com / customer123")
        
        print("\n✅ SEED DATA CREADO EXITOSAMENTE!")
        
    except Exception as e:
        print(f"❌ Error creando seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_intelligent_showtimes(db: Session, movies: list, theaters: list, today: date):
    """Crear horarios inteligentes para las próximas 2 semanas"""
    
    # Horarios estándar por día
    standard_times = [
        {"time": "12:30", "format": ShowtimeFormat.TWO_D_DUBBED},
        {"time": "15:20", "format": ShowtimeFormat.TWO_D_DUBBED},
        {"time": "18:10", "format": ShowtimeFormat.TWO_D_SUBTITLED}, 
        {"time": "21:00", "format": ShowtimeFormat.TWO_D_SUBTITLED},
    ]
    
    # Horarios adicionales para fines de semana
    weekend_times = [
        {"time": "10:00", "format": ShowtimeFormat.TWO_D_DUBBED},
        {"time": "23:00", "format": ShowtimeFormat.TWO_D_SUBTITLED},
    ]
    
    showtimes = []
    
    # Crear horarios para los próximos 14 días
    for day_offset in range(14):
        show_date = today + timedelta(days=day_offset)
        is_weekend = show_date.weekday() >= 5  # Sábado y domingo
        
        # Solo crear horarios para películas en cartelera
        active_movies = [m for m in movies if m.status == MovieStatus.IN_THEATERS]
        
        for movie in active_movies:
            for theater in theaters:
                times_to_use = standard_times + (weekend_times if is_weekend else [])
                
                for schedule in times_to_use:
                    showtime = MovieShowtime(
                        movie_id=movie.id,
                        theater_id=theater.id,
                        show_date=show_date,
                        show_time=schedule["time"],
                        format=schedule["format"],
                        capacity=100,
                        available_tickets=100
                    )
                    showtimes.append(showtime)
    
    db.add_all(showtimes)
    db.commit()
    print(f"✅ {len(showtimes)} horarios creados para los próximos 14 días")


def update_dates_and_showtimes(db: Session):
    """Actualizar fechas de películas y recrear horarios"""
    
    today = date.today()
    
    # Actualizar fechas de películas existentes
    movies = db.query(Movie).all()
    
    for i, movie in enumerate(movies):
        if movie.status == MovieStatus.IN_THEATERS:
            # Películas en cartelera: fechas recientes
            movie.release_date = today - timedelta(days=(i * 3 + 1))
        elif movie.status == MovieStatus.COMING_SOON:
            if movie.is_presale:
                # Preventas: fechas futuras lejanas
                movie.release_date = today + timedelta(days=(40 + i * 7))
            else:
                # Próximos estrenos: fechas futuras cercanas
                movie.release_date = today + timedelta(days=(10 + i * 5))
    
    # Limpiar horarios antiguos
    db.query(MovieShowtime).delete()
    
    # Recrear horarios con fechas actualizadas
    theaters = db.query(Theater).all()
    create_intelligent_showtimes(db, movies, theaters, today)
    
    db.commit()
    print("✅ Fechas y horarios actualizados correctamente")


if __name__ == "__main__":
    create_seed_data()