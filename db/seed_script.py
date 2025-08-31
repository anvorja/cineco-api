# db/seed_script.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.models import User, Movie, UserRole
from app.models.base import Base


def create_seed_data():
    """Create seed data for the cinema application"""

    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Seed data already exists. Skipping...")
            return

        print("Creating seed data...")

        # Create users
        admin_user = User(
            email="admin@cinema.com",
            phone="3501234567",
            first_name="Admin",
            last_name="Cinema",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )

        customer1 = User(
            email="juan.perez@gmail.com",
            phone="3201234567",
            first_name="Juan",
            last_name="Pérez",
            password_hash=get_password_hash("customer123"),
            role=UserRole.CUSTOMER,
            is_active=True
        )

        customer2 = User(
            email="maria.rodriguez@gmail.com",
            phone="3151234567",
            first_name="María",
            last_name="Rodríguez",
            password_hash=get_password_hash("customer123"),
            role=UserRole.CUSTOMER,
            is_active=True
        )

        customer3 = User(
            email="carlos.martinez@hotmail.com",
            phone="3121234567",
            first_name="Carlos",
            last_name="Martínez",
            password_hash=get_password_hash("customer123"),
            role=UserRole.CUSTOMER,
            is_active=True
        )

        db.add_all([admin_user, customer1, customer2, customer3])
        db.flush()

        # Movies data with individual URL fields
        movies_data = [
            {
                "title": "Un Poeta",
                "description": "La obsesión de Óscar Restrepo por la poesía no le trajo ninguna gloria. Envejecido y errático, ha sucumbido al cliché del poeta en la penumbra. Conocer a Yurlady, una humilde adolescente, y ayudarle a cultivar su talento trae algo de luz a sus días, pero arrastrarla al mundo de los poetas tal vez no sea el camino.",
                "genre": "Comedia",
                "duration": 192,
                "rating": "PG-13",
                "price": 18000.0,
                "max_capacity": 120,
                "available_tickets": 120,
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
                "rating": "PG-13",
                "price": 16000.0,
                "max_capacity": 100,
                "available_tickets": 85,
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/3/0/3/0/80303-2-esl-CO/7381965b1505-warner_theconjuring_cinecol_480x670.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/8/0/3/0/80308-2-esl-CO/812a7d6b4522-warner_theconjuring_cinecol_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/6/0/3/0/80306-2-esl-CO/3cbafc21ce34-warner_theconjuring_cinecol_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/7/0/3/0/80307-2-esl-CO/d840c3f43af0-warner_theconjuring_cinecol_510x510.jpg"
            },
            {
                "title": "Black Panther: Wakanda Forever",
                "description": "La reina Ramonda, Shuri, M'Baku, Okoye y las Dora Milaje luchan para proteger su nación tras la muerte del rey T'Challa. Los wakandanos se esfuerzan por abrazar su próximo capítulo.",
                "genre": "Acción",
                "duration": 161,
                "rating": "PG-13",
                "price": 17000.0,
                "max_capacity": 110,
                "available_tickets": 95,
                "poster_url": "https://via.placeholder.com/300x450/9900CC/FFFFFF?text=Black+Panther+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/660099/FFFFFF?text=Black+Panther+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/CC66FF/FFFFFF?text=Black+Panther+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/9900CC/FFFFFF?text=Black+Panther+Detail+2.png"
            },
            {
                "title": "Encanto",
                "description": "Una niña extraordinaria de una familia mágica que vive en una casa mágica en las montañas de Colombia, lucha por demostrar que ella también es especial.",
                "genre": "Animación",
                "duration": 102,
                "rating": "PG",
                "price": 14000.0,
                "max_capacity": 90,
                "available_tickets": 90,
                "poster_url": "https://via.placeholder.com/300x450/FF9900/FFFFFF?text=Encanto+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/FFCC00/000000?text=Encanto+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/FFCC66/000000?text=Encanto+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/FF9900/FFFFFF?text=Encanto+Detail+2.png"
            },
            {
                "title": "Dune",
                "description": "Paul Atreides, un joven brillante y talentoso nacido en un gran destino más allá de su comprensión, debe viajar al planeta más peligroso del universo para asegurar el futuro de su familia y su pueblo.",
                "genre": "Ciencia Ficción",
                "duration": 155,
                "rating": "PG-13",
                "price": 17500.0,
                "max_capacity": 100,
                "available_tickets": 78,
                "poster_url": "https://via.placeholder.com/300x450/CC6600/FFFFFF?text=Dune+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/996633/FFFFFF?text=Dune+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/FFCC99/000000?text=Dune+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/CC6600/FFFFFF?text=Dune+Detail+2.png"
            },
            {
                "title": "Spider-Man: No Way Home",
                "description": "Peter Parker busca la ayuda del Doctor Strange para hacer que el mundo olvide que él es Spider-Man. Sin embargo, el hechizo sale mal y villanos peligrosos de otros universos comienzan a aparecer.",
                "genre": "Acción",
                "duration": 148,
                "rating": "PG-13",
                "price": 16500.0,
                "max_capacity": 110,
                "available_tickets": 65,
                "poster_url": "https://via.placeholder.com/300x450/CC0000/FFFFFF?text=Spider+Man+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/990000/FFFFFF?text=Spider+Man+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/FF3333/FFFFFF?text=Spider+Man+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/CC0000/FFFFFF?text=Spider+Man+Detail+2.png"
            },
            {
                "title": "The Batman",
                "description": "En su segundo año luchando contra el crimen, Batman desentraña la corrupción en Gotham City que conecta con su propia familia mientras se enfrenta a un asesino en serie conocido como El Acertijo.",
                "genre": "Acción",
                "duration": 176,
                "rating": "PG-13",
                "price": 17000.0,
                "max_capacity": 100,
                "available_tickets": 82,
                "poster_url": "https://via.placeholder.com/300x450/333333/FFFFFF?text=Batman+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/000000/FFFFFF?text=Batman+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/666666/FFFFFF?text=Batman+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/333333/FFFFFF?text=Batman+Detail+2.png"
            },
            {
                "title": "Frozen II",
                "description": "Elsa, Anna, Kristoff y Olaf se adentran en el bosque otoñal para encontrar el origen de los poderes mágicos de Elsa y salvar su reino.",
                "genre": "Animación",
                "duration": 103,
                "rating": "PG",
                "price": 14500.0,
                "max_capacity": 80,
                "available_tickets": 80,
                "poster_url": "https://via.placeholder.com/300x450/66CCFF/FFFFFF?text=Frozen+2+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/3399CC/FFFFFF?text=Frozen+2+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/99DDFF/000000?text=Frozen+2+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/66CCFF/FFFFFF?text=Frozen+2+Detail+2.png"
            },
            {
                "title": "Jurassic World: Dominion",
                "description": "Cuatro años después de la destrucción de Isla Nublar, los dinosaurios ahora viven y cazan junto a los humanos en todo el mundo. Este frágil equilibrio remodelará el futuro.",
                "genre": "Aventura",
                "duration": 147,
                "rating": "PG-13",
                "price": 16000.0,
                "max_capacity": 105,
                "available_tickets": 72,
                "poster_url": "https://via.placeholder.com/300x450/669900/FFFFFF?text=Jurassic+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/336600/FFFFFF?text=Jurassic+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/99CC33/000000?text=Jurassic+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/669900/FFFFFF?text=Jurassic+Detail+2.png"
            },
            {
                "title": "Minions: The Rise of Gru",
                "description": "En los años 70, Gru crece en los suburbios, siendo un gran fan de un grupo de supervillanos conocidos como los Vicious 6. Para demostrar que es malvado, Gru idea un plan para unirse a ellos.",
                "genre": "Animación",
                "duration": 87,
                "rating": "PG",
                "price": 13000.0,
                "max_capacity": 85,
                "available_tickets": 85,
                "poster_url": "https://via.placeholder.com/300x450/FFFF00/000000?text=Minions+Poster.png",
                "backdrop_url": "https://via.placeholder.com/1920x1080/CCCC00/000000?text=Minions+Backdrop.png",
                "detail_1_url": "https://via.placeholder.com/600x400/FFFF66/000000?text=Minions+Detail+1.png",
                "detail_2_url": "https://via.placeholder.com/600x400/FFFF00/000000?text=Minions+Detail+2.png"
            }
        ]

        # Create movie objects
        movies = []
        for movie_data in movies_data:
            movie = Movie(**movie_data)
            movies.append(movie)

        db.add_all(movies)
        db.commit()

        print(f"Seed data created successfully!")
        print(f"- Created {len([admin_user, customer1, customer2, customer3])} users")
        print(f"- Created {len(movies)} movies")
        print(f"\nLogin credentials:")
        print(f"Admin: admin@cinema.com / admin123")
        print(f"Customer 1: juan.perez@gmail.com / customer123")
        print(f"Customer 2: maria.rodriguez@gmail.com / customer123")
        print(f"Customer 3: carlos.martinez@hotmail.com / customer123")

    except Exception as e:
        print(f"Error creating seed data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
