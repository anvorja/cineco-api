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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/1/6/9/9/79961-1-esl-CO/2a0d94e039d9-poster480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/6/6/9/9/79966-1-esl-CO/8615e7249c91-postertrailer100x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/6/9/9/79964-1-esl-CO/e413e41a5920-banizq510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/9/9/79965-1-esl-CO/2921f1428698-bander510.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/0/5/6/9/79650-1-esl-CO/a0899049400e-480x670_poster_cinecolombia.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/5/5/6/9/79655-1-esl-CO/f4815e2d6412-1000x510_imagentrailer_cinecolombia.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/3/5/6/9/79653-1-esl-CO/9da770cbc18f-510x511_bannerizq_cinecolombia.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/5/6/9/79654-1-esl-CO/e0473ced12c9-510x510_bannerder_cinecolombia.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/7/5/4/0/80457-1-esl-CO/b9fbdaa8607e-480x670-9-.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/2/6/4/0/80462-1-esl-CO/a9300cc64c44-1000x510-11-.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/0/6/4/0/80460-1-esl-CO/c313573a01ba-510x510-9-.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/1/6/4/0/80461-1-esl-CO/7fbe14fda17d-510x510-9-.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/8/3/4/1/81438-2-esl-CO/db9a40298079-poster-oficial_-480x670-.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/3/4/4/1/81443-1-esl-CO/175146b755c6-trailer_-1000x510-.png",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/1/4/4/1/81441-1-esl-CO/e803866132d9-banner_izq_-510x510-.png",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/2/4/4/1/81442-1-esl-CO/f1515c39318d-banner_drcho_-510x510-.png"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/4/6/7/9/79764-1-esl-CO/f720651fc698-480x670_poster_interna_cinecolombia.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/9/6/7/9/79769-1-esl-CO/e5124787ae08-1000x510_sin_texto_img-a-la-derecha-imagentrailer_cinecolombia.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/7/6/7/9/79767-1-esl-CO/839b45023c84-510x511_bannerizq_cinecolombia.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/8/6/7/9/79768-1-esl-CO/589f0d946329-510x510_bannerder_cinecolombia.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/2/6/3/1/81362-1-esl-CO/c0eb13751ac8-ar-banner-web-480x670px-fecha.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/7/6/3/1/81367-1-esl-CO/647fe2937b8f-ar-3-imagen-trailer.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/6/3/1/81365-1-esl-CO/b04b6ebe747b-ar-4-banner-izquierdo.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/6/6/3/1/81366-1-esl-CO/a5b4f60b7b26-ar-5-banner-derecho.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/8/8/6/9/79688-1-esl-CO/2f37f371a830-warner_weapons_cinecol_480x670.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/3/9/6/9/79693-1-esl-CO/53305451b0f6-warner_weapons_cinecol_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/1/9/6/9/79691-1-esl-CO/e4ce6ac559eb-warner_weapons_cinecol_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/2/9/6/9/79692-1-esl-CO/620e3ad9fe89-warner_weapons_cinecol_510x510.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/0/9/7/0/80790-1-esl-CO/b95d013a97e1-2b-poster.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/5/9/7/0/80795-1-esl-CO/1747590dc672-3a-imagentrailer.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/3/9/7/0/80793-1-esl-CO/04d4ea723cc3-4-5a-bannerizqder.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/9/7/0/80794-1-esl-CO/a2f85add2d51-4-5b-bannerizqder.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/0/9/8/6/76890-5-esl-CO/101b0233f37f-480x670_poster_cinecolombia.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/5/9/8/6/76895-5-esl-CO/bf7d06ba02a8-1024x512_bannertw_cinecolombia.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/3/9/8/6/76893-4-esl-CO/e00131d79367-510x511_bannerizq_cinecolombia.png",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/9/8/6/76894-4-esl-CO/46267e96e0f8-510x510_bannerder_cinecolombia.png"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/6/7/6/0/80676-1-esl-CO/7fea5c8ecb42-hqr-banner-web-480x670px-exc.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/1/8/6/0/80681-1-esl-CO/683ac201f76f-hqr-3-imagen-trailer.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/9/7/6/0/80679-1-esl-CO/78a139888b70-hqr-5-banner-derecho.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/0/8/6/0/80680-1-esl-CO/306f15213f0f-hqr-5-banner-derecho.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/0/4/8/9/79840-1-esl-CO/569e08973200-2_poster_480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/5/4/8/9/79845-1-esl-CO/488504e5ff77-3_imagentrailer_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/3/4/8/9/79843-1-esl-CO/5dcc5c51629e-4_bannerizq_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/4/4/8/9/79844-1-esl-CO/48f72947e827-5_bannerder_510x510.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/8/5/0/1/81058-1-esl-CO/d7da051741b6-poster_-480x670-.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/3/6/0/1/81063-1-esl-CO/7e4f1fe2f3ed-trailer_-1000x510-.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/1/6/0/1/81061-1-esl-CO/5b002b9bc01b-banner_izq_-510x510-.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/2/6/0/1/81062-1-esl-CO/fe0851687daf-banner_drcho_-510x510-.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/8/6/8/0/80868-1-esl-CO/50735f987c14-2_poster_480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/3/7/8/0/80873-1-esl-CO/0faed51bf1db-3_imagentrailer_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/1/7/8/0/80871-1-esl-CO/79ef50ab69e8-4_bannerizq_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/2/7/8/0/80872-1-esl-CO/c5f9c6ce4b75-5_bannerder_510x510.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/4/3/1/1/81134-1-esl-CO/1e969ab06d4b-split_cineco_pstr-dskp_480x670.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/9/3/1/1/81139-1-esl-CO/015d4da14f26-split_cineco_bnnr-trlr_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/7/3/1/1/81137-1-esl-CO/246eb389a66c-split_cineco_bnnr-izq_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/7/3/1/1/81137-1-esl-CO/246eb389a66c-split_cineco_bnnr-izq_510x510.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/2/7/1/1/81172-2-esl-CO/b786f838a5a1-mistura_poster_peru_colombia_layers_61225.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/7/7/1/1/81177-1-esl-CO/2bdf8318cc67-mistura1000x510_sin_texto_img-a-la-derecha-imagentrailer_cinecolombia.png",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/5/7/1/1/81175-1-esl-CO/63dadb6601a3-mistura510x511_bannerizq_cinecolombia.png",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/6/7/1/1/81176-1-esl-CO/90bf61294950-mistura510x510_bannerder_cinecolombia.png"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/9/8/1/0/80189-1-esl-CO/3b80932784bd-2_poster_480x670.png",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/4/9/1/0/80194-1-esl-CO/09bda886e8ce-3_imagentrailer_1000x510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/2/9/1/0/80192-1-esl-CO/3b0db9ae128a-4_bannerizq_510x510.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/3/9/1/0/80193-1-esl-CO/c588c4bde4c5-5_bannerder_510x510.jpg"
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
                "poster_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_poster/4/1/5/1/81514-5-esl-CO/86ced68cb262-2017_bts_wingstour_480-x-670.jpg",
                "backdrop_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_embed/9/1/5/1/81519-5-esl-CO/852afaa101c0-2017_bts_wingstour_1000-x-510.jpg",
                "detail_1_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/9/7/4/1/81479-1-esl-CO/2d902bb0036f-bts-movie-weeks.jpg",
                "detail_2_url": "https://archivos-cms.cinecolombia.com/images/_aliases/exhibition_split_banner/9/7/4/1/81479-1-esl-CO/2d902bb0036f-bts-movie-weeks.jpg"
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