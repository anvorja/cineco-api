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
    """Crear datos de seed completos con horarios optimizados"""
    
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
                email="andres.vorja.vorja@gmail.com",
                phone="3201234567",
                first_name="Andres",
                last_name="Borja",
                password_hash=get_password_hash("demo123"),
                role=UserRole.CUSTOMER,
                is_active=True
            ),
            User(
                email="maria.rodriguez@gmail.com",
                phone="3151234567",
                first_name="María",
                last_name="Rodríguez",
                password_hash=get_password_hash("demo123"),
                role=UserRole.CUSTOMER,
                is_active=True
            ),
            User(
                email="carlos.martinez@hotmail.com",
                phone="3121234567",
                first_name="Carlos",
                last_name="Martínez",
                password_hash=get_password_hash("demo123"),
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
                "location": "C.C. Unicentro, Cali",
                "description": "Cine moderno con zona de juegos"
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
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Otro Viernes de Locos",
                "description": "Años después de que Tess y Anna sufrieran una crisis de identidad, Anna tiene una hija y pronto una hijastra. Mientras afrontan los retos que surgen cuando dos familias se fusionan, Tess y Anna descubren que un rayo puede caer dos veces.",
                "genre": "Comedia",
                "duration": 111,
                "rating": "R",
                "price": 20000.0,
                "director": "Nisha Ganatra",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=24),  # Estrenada hace 24 días
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Sketch Dibujos Animados",
                "description": "Un fotógrafo promete poner a su amada en la portada de la revista Look para obtener la aprobación del padre, pero cumplir esta promesa resulta complicado.",
                "genre": "Aventura, Comedia, Fantasia",
                "duration": 93,
                "rating": "PG-13",
                "price": 22000.0,
                "director": "Seth Worley",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "La Colina de las Amapolas",
                "description": "Japón, año 1963. Umi Matsuzaki es una estudiante de instituto que, en ausencia de su madre, cuida a sus dos hermanos y de su abuela a la par que administra un hostal de estilo occidental, el Coquelicot Manor, en lo alto de una colina y cercano al mar. La chica compagina tranquilamente sus responsabilidades con su vida escolar. Un día conoce a Shun Kazama, miembro del club de periodismo, y Shiro Mizunuma, presidente del consejo de estudiantes. Ambos son representantes del Quartier Latin, un edificio antiguo que alberga las diferentes asociaciones de estudiantes y que corre el peligro de ser demolido. Entre Umi y Kazama surgirá una profunda amistad que podría verse complicada con el inesperado descubrimiento de un secreto del pasado. Juntos descubrirán una forma de convivir entre el turbio pasado, el difícil presente y el esperanzador futuro en un momento del tiempo donde el Japón empezaba a levantar cabeza.",
                "genre": "Aventura, Fantasia, Anime",
                "duration": 91,
                "rating": "PG-13",
                "price": 22000.0,
                "director": "Goro Miyazaki",
                "country": "Japón",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Los Roses",
                "description": "Los celos de una pareja aparentemente perfecta estallan cuando la carrera profesional del marido implosiona, revelando grietas en la fachada de su vida familiar ideal.",
                "genre": "Comedia, Drama",
                "duration": 120,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Jay Roach",
                "country": "Reino Unido, Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),  # Estrenada hace 3 días
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Atrapado Robando",
                "description": "Hank Thompson (Austin Butler) era un fenómeno del béisbol en la preparatoria que ya no puede jugar, pero en todo lo demás le va bien. Tiene una chica estupenda (Zoë Kravitz), es mesero en un antro de Nueva York y su equipo favorito está en racha. \n Cuando su vecino punk-rock, Russ (Matt Smith), le pide que cuide de su gato durante unos días, Hank se ve de repente atrapado en medio de un grupo de gángsters amenazadores. Todos quieren algo de él; el problema es que no sabe por qué. Mientras Hank intenta eludir sus cada vez más apretadas garras, tendrá que emplear todas sus habilidades para mantenerse con vida el tiempo suficiente para averiguarlo.",
                "genre": "Crimen",
                "duration": 120,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Darren Aronofsky",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),  # Estrenada hace 3 días
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "La Hora de la Desaparición",
                "description": "Una epopeya de terror de varias historias interrelacionadas sobre la desaparición de estudiantes de instituto en una pequeña ciudad.",
                "genre": "Misterio, Horror",
                "duration": 120,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Zach Cregger",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),  # Estrenada hace 3 días
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "La Creación De Los Dioses: El Reino",
                "description": "Una magnífica epopeya de alta fantasía oriental que recrea las prolongadas guerras míticas entre humanos, inmortales y monstruos, ocurridas hace más de tres mil años.",
                "genre": "Acción, Aventura",
                "duration": 120,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Wuershan",
                "country": "China",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=3),  # Estrenada hace 3 días
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Los 4 Fantásticos: Primeros pasos",
                "description": "La primera familia de Marvel se enfrenta a su mayor desafío hasta la fecha. Obligados a equilibrar su papel de héroes con la fuerza de su vínculo familiar, deben defender la Tierra de un voraz dios del espacio llamado Galactus.",
                "genre": "Acción, Aventura, Ciencia Ficción",
                "duration": 115,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Matt Shakman",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=7),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Haz que regrese",
                "description": "Una hermano y una hermana descubren un ritual aterrador en la aislada casa de su nueva madre adoptiva.",
                "genre": "Terror",
                "duration": 104,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Danny Philippou; Michael Philippou",
                "country": "Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=7),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Drácula",
                "description": "Del visionario director Luc Besson (El quinto elemento, El perfecto asesino, Lucy) llega a la pantalla grande la obra maestra de Bram Stoker, DRÁCULA. \n Una pasión prohibida atraviesa los siglos. Después de perder a su gran amor, Vlad hace un pacto oscuro que lo condena a la eternidad como Drácula. Siglos después, en la Inglaterra victoriana, una joven idéntica a su amada renace su esperanza... y su maldición. \n Una historia gótica de deseo, redención y el poder inmortal del amor.",
                "genre": "Fantasia, Romance, Terror",
                "duration": 129,
                "rating": "PG-13",
                "price": 18000.0,
                "director": "Luc Besson",
                "country": "Francia, Estados Unidos",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today - timedelta(days=17),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
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
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            # PRÓXIMOS ESTRENOS
            {
                "title": "La Hermanastra Fea",
                "description": "Un giro aterrador y sangriento al clásico cuento de Cenicienta, LA HERMANASTRA FEA cuenta la historia de Elvira, la hermanastra, mientras se prepara para ganarse el afecto del príncipe. En un reino donde la belleza es un asunto brutal, Elvira estará dispuesta a todo por competir con la bella y encantadora Cenicienta, para convertirse en la reina del baile y la más bella del reino.",
                "genre": "Terror",
                "duration": 101,
                "rating": "PG-13",
                "price": 22000.0,
                "director": "Emilie Blichfeldt",
                "country": "Dinamarca, Noruega, Rumania",
                "status": MovieStatus.IN_THEATERS,
                "is_presale": False,
                "release_date": today + timedelta(days=10),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Putin",
                "description": "Ambientada en un futuro cercano, Putin ofrece una visión estilizada del meteórico ascenso y la devastadora caída de Vladimir Putin. Utilizando tecnología de vanguardia, el retrato poco convencional de Patryck Vega sobre el enigmático dictador explora la tumultuosa transformación de Putin, desde su infancia problemática hasta su implacable ascenso al poder, y examina cómo esa brutal ambición también podría sembrar las semillas de su propia destrucción.",
                "genre": "Drama, Suspenso, Biografía",
                "duration": 100,
                "rating": "PG-13",
                "price": 23000.0,
                "director": "Patryk Vega",
                "country": "Polonia",
                "status": MovieStatus.COMING_SOON,
                "is_presale": False,
                "release_date": today + timedelta(days=4),  # Estreno en 4 dias
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Amores Compartidos",
                "description": "Cuando Ashley le pide el divorcio, el bonachón de Carey acude a sus amigos Julie y Paul. Su secreto para la felicidad es un matrimonio abierto; es decir, hasta que Carey cruza la línea y hace que todas sus relaciones sean un caos.",
                "genre": "Comedia",
                "duration": 161,
                "rating": "PG-13",
                "price": 23000.0,
                "director": "Michael Angelo Covino",
                "country": "Estados Unidos",
                "status": MovieStatus.COMING_SOON,
                "is_presale": False,
                "release_date": today + timedelta(days=10),
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Mistura",
                "description": "La vida de una mujer se desmorona después de que la traición de su marido la aísla de la sociedad de élite. Al acoger a comunidades marginadas, se embarca en un viaje transformador, desafiando las normas a través de una atrevida aventura culinaria que redefine su vida.",
                "genre": "Drama",
                "duration": 161,
                "rating": "PG-13",
                "price": 23000.0,
                "director": "Ricardo de Montreuil",
                "country": "Peru",
                "status": MovieStatus.COMING_SOON,
                "is_presale": False,
                "release_date": today + timedelta(days=10),  # Estreno en 4 dias
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            {
                "title": "Camina o Muere",
                "description": "De la esperada adaptación de la primera novela escrita por el maestro narrador Stephen King,y Francis Lawrence, el director visionario de las películas de la franquicia Los Juegos del Hambre (En llamas, Sinsajo - Partes 1 y 2, y La balada de los pájaros cantores y las serpientes), llega The Long Walk/ Camina o Muere, un thriller intenso, escalofriante y emotivo que desafía al público a enfrentar una pregunta inquietante: \n ¿Hasta dónde serías capaz de llegar?",
                "genre": "Terror, Thriller",
                "duration": 161,
                "rating": "PG-13",
                "price": 23000.0,
                "director": "Francis Lawrence",
                "country": "Estados Unidos",
                "status": MovieStatus.COMING_SOON,
                "is_presale": False,
                "release_date": today + timedelta(days=17),  # Estreno en 4 dias
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
            },
            # PREVENTAS
            {
                "title": "BTS 2017 Live Trilogy EPISODE III THE WINGS TOUR THE FINAL Remastered",
                "description": 'BTS consolidó su prestigio mundial con su primer premio Billboard Music Award, y su meteórico ascenso queda plasmado con fuerza en ""BTS 2017 Live Trilogy EPISODE III THE WINGS TOUR THE FINAL Remastered. \n Las actuaciones individuales y grupales revelan múltiples matices a través de voces aterciopeladas y rap poético, mientras que las electrizantes interpretaciones de “Blood Sweat & Tears”, “DNA” y “MIC Drop” reflejan las dimensiones que alcanzó esta gira.',
                "genre": "Concierto",
                "duration": 170,
                "rating": "PG-13",
                "price": 24000.0,
                "director": "Kim Sanguk",
                "country": "República de Corea",
                "status": MovieStatus.COMING_SOON,
                "is_presale": True,
                "release_date": today + timedelta(days=52),  # Estreno en 7+ semanas
                "poster_url": "https://placehold.co/480x670.png",
                "backdrop_url": "https://placehold.co/1000x510.png",
                "detail_1_url": "https://placehold.co/510x510.png",
                "detail_2_url": "https://placehold.co/510x510.png"
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
    """Crear horarios inteligentes optimizados - 3 horarios por teatro por día"""

    # 🎯 HORARIOS FIJOS Y SIMPLES POR DÍA
    # Solo 3 horarios estándar para mantener simplicidad
    standard_times = [
        {"time": "15:20", "format": ShowtimeFormat.TWO_D_DUBBED},
        {"time": "18:10", "format": ShowtimeFormat.TWO_D_SUBTITLED},
        {"time": "21:00", "format": ShowtimeFormat.TWO_D_SUBTITLED},
    ]

    showtimes = []
    
    # Horarios adicionales para fines de semana
    weekend_times = [
        {"time": "10:00", "format": ShowtimeFormat.TWO_D_DUBBED},
        {"time": "23:00", "format": ShowtimeFormat.TWO_D_SUBTITLED},
    ]
    
    showtimes = []

    # Crear horarios para los próximos 14 días
    for day_offset in range(14):
        show_date = today + timedelta(days=day_offset)

        # Solo películas en cartelera
        active_movies = [m for m in movies if m.status == MovieStatus.IN_THEATERS]

        # 🔄 ROTACIÓN SIMPLE: Una película diferente por teatro cada día
        for theater_index, theater in enumerate(theaters):
            # Rotar películas por teatro para distribución equilibrada
            movie_index = (day_offset + theater_index) % len(active_movies)
            selected_movie = active_movies[movie_index]

            # Solo 3 horarios por teatro por día
            for schedule in standard_times:
                showtime = MovieShowtime(
                    movie_id=selected_movie.id,
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
    print(f"✅ {len(showtimes)} horarios creados (3 por teatro por día)")

    # 📊 Estadísticas de validación
    total_days = 14
    total_theaters = len(theaters)
    expected_total = total_days * total_theaters * 3  # 3 horarios por teatro por día

    print(f"📈 Validación de horarios:")
    print(f"   - Días: {total_days}")
    print(f"   - Teatros: {total_theaters}")
    print(f"   - Horarios por teatro/día: 3")
    print(f"   - Total esperado: {expected_total}")
    print(f"   - Total creado: {len(showtimes)}")

    if len(showtimes) == expected_total:
        print("✅ Horarios creados correctamente")
    else:
        print("⚠️  Discrepancia en cantidad de horarios")


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
