import asyncio
import sys
import os
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
import uuid

# Asegurarse de que el script pueda encontrar los módulos de la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import AsyncSessionLocal, async_engine
from app.db.models.user import User
from app.db.models.blog_post import BlogPost # Necesario para comprobar slugs existentes
from app.schemas.blog import BlogPostCreate
from app.crud.crud_blog import create_blog_post, get_blog_post_by_slug, slugify # Importar slugify

# Datos extraídos de frontend/src/lib/linkedin-posts-data.ts
raw_linkedin_posts: List[Dict[str, Any]] = [
  {
    "id": "li-flora-photoshop",
    "url": "https://www.linkedin.com/posts/eric-vyacheslav-156273169_chatgpt-4o-flora-just-killed-photoshop-ugcPost-7322702227528105984-H94n",
    "description": "ChatGPT-4o Flora vs Photoshop",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322702227528105984?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2025-04-13",
    "category": "IA Generativa",
    "author": "recommended"
  },
  {
    "id": "li-ai-agents",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ai-agents-activity-7322529580295110656-dCBf",
    "description": "AI Agents",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322529340309549059?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2025-04-28",
    "category": "Agentes IA",
    "author": "me"
  },
   {
    "id": "li-audio-driven-video",
    "url": "https://www.linkedin.com/posts/alessandroperrilli_emo-audio-driven-video-avatar-ugcPost-7169728132965384192-xZgT",
    "description": "EMO: Audio-Driven Video Avatar",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2025-02-04",
    "category": "IA Generativa",
    "author": "recommended"
  },
  {
    "id": "li-suenos",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_este-siempre-ha-sido-uno-de-mis-sue%C3%B1os-activity-7254226595668774912-5-LM",
    "description": "Uno de mis sueños",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7254024202280706050?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-11-04",
    "category": "VR/AR",
    "author": "me"
  },
  {
    "id": "li-immersia-team",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_immersia-immersianos-weareimmersians-activity-7250138812738093058-iBKy",
    "description": "Equipo Immersia",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:share:7250120840480968705?collapsed=1" height="265" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-11-04",
    "category": "Equipo/Cultura",
    "author": "me"
  },
  {
    "id": "li-reinforcement-learning",
    "url": "https://www.linkedin.com/posts/imarpit_ai-reinforcementlearning-machinelearning-ugcPost-7219951802492874752-fTcz",
    "description": "Reinforcement Learning",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7219951802492874752?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-08-04",
    "category": "Aprendizaje Automático",
    "author": "recommended"
  },
  {
    "id": "li-future-of-work",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ive-been-thinking-a-lot-about-the-future-activity-7217659492472107009--ifb",
    "description": "Futuro del Trabajo",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7216163666256179202?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-05-04",
    "category": "Futuro del Trabajo",
    "author": "me"
  },
  {
    "id": "li-tokii-vr-immersia",
    "url": "https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un",
    "description": "Tokii VR (Immersia)",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-05-04",
    "category": "Educación IA/VR",
    "author": "me"
  },
  {
    "id": "li-neural-net-graphical",
    "url": "https://www.linkedin.com/posts/eric-vyacheslav-156273169_amazing-graphical-representation-of-a-neural-ugcPost-7274785920447320065-EPL4",
    "description": "Neural Net Graphical Representation",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7274785920447320065?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2025-01-04",
    "category": "Visualización IA",
    "author": "recommended"
  },
  {
    "id": "li-immersia-visit",
    "url": "https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un",
    "description": "Visita Delegación Japonesa",
    "embedCode": "<iframe src=\"https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1\" height=\"543\" width=\"504\" frameborder=\"0\" allowfullscreen=\"\" title=\"Publicación integrada\"></iframe>",
    "publishedDate": "2025-04-27",
    "category": "Equipo/Cultura",
    "author": "me"
  },
  {
    "id": "li-ai-glasses-privacy",
    "url": "https://www.linkedin.com/posts/endritrestelica_rip-privacy-this-guy-used-ai-powered-glasses-ugcPost-7320915912096657412-jeBW",
    "description": "AI Powered Glasses Privacy",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7320915912096657412?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2025-04-27",
    "category": "Privacidad IA",
    "author": "recommended"
  },
  {
    "id": "li-visionarynet-ai",
    "url": "https://www.linkedin.com/posts/visionarynet_artificialintelligence-machinelearning-ml-ugcPost-7288501315444363264-lEa2",
    "description": "VisionaryNet AI",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7288501315444363264?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-04-10",
    "category": "IA Generativa",
    "author": "recommended"
  },
   {
    "id": "li-smartglass-ai",
    "url": "https://www.linkedin.com/posts/smartglassnews_ai-tech-innovation-ugcPost-7170174855294730241-Bv4z",
    "description": "SmartGlass AI",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Publicación integrada"></iframe>',
    "publishedDate": "2024-02-25",
    "category": "Hardware/Dispositivos",
    "author": "recommended"
   }
]

async def main():
    print("Inicio del script de migración de posts de LinkedIn...")
    db: AsyncSession = AsyncSessionLocal()
    try:
        # 1. Encontrar el primer superusuario
        stmt = select(User).filter(User.is_superuser == True).limit(1)
        result = await db.execute(stmt)
        superuser = result.scalars().first()

        if not superuser:
            print("Error: No se encontró ningún superusuario. Asigne un superusuario antes de ejecutar el script.")
            print("Puede hacerlo directamente en la base de datos o a través de la lógica de su aplicación.")
            return

        print(f"Superusuario encontrado: {superuser.email} (ID: {superuser.id})")

        migrated_count = 0
        skipped_count = 0
        placeholder_embed_code = "<!-- PEGA AQUÍ EL CÓDIGO EMBED -->"

        for post_data in raw_linkedin_posts:
            if post_data["embedCode"] == placeholder_embed_code:
                print(f"Skipping post ID '{post_data['id']}' debido a embed code placeholder.")
                skipped_count += 1
                continue
            
            # 2. Transformar datos
            title = post_data["description"]
            # Asegurar que el título no sea excesivamente largo para un slug
            if len(title) > 200:
                title = title[:200] + "..."
            
            content = post_data["description"] # Usar descripción como contenido principal
            excerpt = post_data["description"][:250] if len(post_data["description"]) > 250 else post_data["description"] # Un extracto más largo
            
            tags = post_data["category"]
            linkedin_url = post_data["embedCode"] # Este es el código de embebido
            
            # Convertir publishedDate string a objeto date
            try:
                published_dt_obj = datetime.strptime(post_data["publishedDate"], "%Y-%m-%d").date()
            except ValueError:
                print(f"Error: Fecha inválida '{post_data['publishedDate']}' para el post ID '{post_data['id']}'. Saltando este post.")
                skipped_count += 1
                continue

            blog_post_in = BlogPostCreate(
                title=title,
                content=content,
                excerpt=excerpt,
                tags=tags,
                image_url=None, # Los posts de LinkedIn embebidos no necesitan una imagen separada
                linkedin_post_url=linkedin_url,
                status="published"
            )

            # 3. Comprobar si ya existe un post con el mismo slug (generado a partir del título)
            # La función create_blog_post ya genera el slug.
            # Sin embargo, para este script, es bueno verificarlo ANTES para no fallar a mitad.
            # La función crud create_blog_post NO sobreescribe published_date, lo cual es bueno aquí.
            
            temp_slug = slugify(blog_post_in.title)
            existing_post_by_slug = await get_blog_post_by_slug(db, slug=temp_slug)
            if existing_post_by_slug:
                print(f"Skipping post with title '{blog_post_in.title}' (slug: '{temp_slug}') porque ya existe un post con ese slug.")
                skipped_count += 1
                continue

            # 4. Crear y guardar el blog post
            # La función `create_blog_post` en crud_blog.py se encarga de:
            # - Generar ID
            # - Generar Slug (ya lo comprobamos arriba, pero la función lo hará formalmente)
            # - Establecer published_date (¡OJO! Lo queremos controlar desde el script)
            # - Establecer author_id
            
            # Modificamos la llamada a create_blog_post para pasar también la published_date
            # Esto requiere que ajustemos `crud.blog.create_blog_post` o creemos una versión para el script.
            # Por simplicidad, vamos a crear el objeto BlogPost directamente aquí y añadirlo.
            
            new_id = uuid.uuid4().hex # Importar uuid
            
            db_blog_post = BlogPost(
                **blog_post_in.dict(exclude_unset=True), # Pasa los campos de BlogPostCreate
                id=new_id,
                slug=temp_slug, # Usamos el slug que ya verificamos
                author_id=superuser.id,
                published_date=published_dt_obj # Usar la fecha de publicación del post original
                # last_modified_date se actualizará automáticamente si está configurado en el modelo
            )
            
            db.add(db_blog_post)
            await db.commit()
            await db.refresh(db_blog_post)
            
            print(f"Post '{db_blog_post.title}' (ID: {db_blog_post.id}, Slug: {db_blog_post.slug}) creado con fecha de publicación: {db_blog_post.published_date}")
            migrated_count += 1

    except Exception as e:
        print(f"Ocurrió un error durante la migración: {e}")
        await db.rollback() # Asegurar rollback en caso de error general
    finally:
        await db.close()
        await async_engine.dispose() # MODIFICADO AQUÍ

    print(f"--- Resumen de la Migración ---")
    print(f"Posts migrados exitosamente: {migrated_count}")
    print(f"Posts omitidos (placeholder o ya existentes o error de fecha): {skipped_count}")
    print("Script de migración finalizado.")

if __name__ == "__main__":
    asyncio.run(main()) 