import asyncio
from sqlalchemy.future import select

# Importar la sesión, modelos y datos iniciales
# Asegúrate de que la estructura de imports funciona desde la raíz del backend
from app.db.session import AsyncSessionLocal, async_engine
from app.db.models import Project, BlogPost, NewsItem 
from app.db.initial_data import initial_projects, initial_blog_posts, initial_news_items
from app.db.base import Base # Necesario para crear tablas si no existen

async def seed_database():
    print("Iniciando script de inicialización de base de datos...")
    
    # Asegurarse de que las tablas existen (opcional, main.py ya lo hace)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        try:
            print("Comprobando datos existentes...")
            
            # Comprobar Proyectos
            result_projects = await db.execute(select(Project).limit(1))
            if not result_projects.scalars().first():
                print("No hay proyectos, insertando datos iniciales...")
                projects_to_add = [Project(**data) for data in initial_projects]
                db.add_all(projects_to_add)
                await db.commit()
                print(f"Insertados {len(projects_to_add)} proyectos.")
            else:
                print("Ya existen proyectos, saltando inserción.")

            # Comprobar Posts del Blog
            result_posts = await db.execute(select(BlogPost).limit(1))
            if not result_posts.scalars().first():
                print("No hay posts de blog, insertando datos iniciales...")
                posts_to_add = [BlogPost(**data) for data in initial_blog_posts]
                db.add_all(posts_to_add)
                await db.commit()
                print(f"Insertados {len(posts_to_add)} posts de blog.")
            else:
                print("Ya existen posts de blog, saltando inserción.")

            # Comprobar Noticias
            result_news = await db.execute(select(NewsItem).limit(1))
            if not result_news.scalars().first():
                print("No hay noticias, insertando datos iniciales...")
                news_to_add = [NewsItem(**data) for data in initial_news_items]
                db.add_all(news_to_add)
                await db.commit()
                print(f"Insertadas {len(news_to_add)} noticias.")
            else:
                print("Ya existen noticias, saltando inserción.")

            print("--- Script de inicialización completado --- ")

        except Exception as e:
            print(f"Ocurrió un error durante la inicialización: {e}")
            await db.rollback() # Revertir cambios en caso de error
        finally:
            await db.close()

if __name__ == "__main__":
    print("Ejecutando seed_database...")
    asyncio.run(seed_database()) 