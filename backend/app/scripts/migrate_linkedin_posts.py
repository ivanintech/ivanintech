import asyncio
import sys
import os
from typing import List, Dict, Any
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, datetime
import uuid

# Ensure the script can find the app's modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import AsyncSessionLocal, async_engine
from app.db.models.user import User
from app.db.models.blog_post import BlogPost # Needed to check for existing slugs
from app.schemas.blog import BlogPostCreate
from app.crud.crud_blog import create_blog_post, get_blog_post_by_slug, slugify # Import slugify

# Data extracted from frontend/src/lib/linkedin-posts-data.ts
raw_linkedin_posts: List[Dict[str, Any]] = [
  {
    "id": "li-flora-photoshop",
    "url": "https://www.linkedin.com/posts/eric-vyacheslav-156273169_chatgpt-4o-flora-just-killed-photoshop-ugcPost-7322702227528105984-H94n",
    "description": "ChatGPT-4o Flora vs Photoshop",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322702227528105984?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2025-04-13",
    "category": "Generative AI",
    "author": "recommended"
  },
  {
    "id": "li-ai-agents",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ai-agents-activity-7322529580295110656-dCBf",
    "description": "AI Agents",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7322529340309549059?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2025-04-28",
    "category": "AI Agents",
    "author": "me"
  },
   {
    "id": "li-audio-driven-video",
    "url": "https://www.linkedin.com/posts/alessandroperrilli_emo-audio-driven-video-avatar-ugcPost-7169728132965384192-xZgT",
    "description": "EMO: Audio-Driven Video Avatar",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2025-02-04",
    "category": "Generative AI",
    "author": "recommended"
  },
  {
    "id": "li-suenos",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_este-siempre-ha-sido-uno-de-mis-sue%C3%B1os-activity-7254226595668774912-5-LM",
    "description": "One of my dreams",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7254024202280706050?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-11-04",
    "category": "VR/AR",
    "author": "me"
  },
  {
    "id": "li-immersia-team",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_immersia-immersianos-weareimmersians-activity-7250138812738093058-iBKy",
    "description": "Immersia Team",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:share:7250120840480968705?collapsed=1" height="265" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-11-04",
    "category": "Team/Culture",
    "author": "me"
  },
  {
    "id": "li-reinforcement-learning",
    "url": "https://www.linkedin.com/posts/imarpit_ai-reinforcementlearning-machinelearning-ugcPost-7219951802492874752-fTcz",
    "description": "Reinforcement Learning",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7219951802492874752?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-08-04",
    "category": "Machine Learning",
    "author": "recommended"
  },
  {
    "id": "li-future-of-work",
    "url": "https://www.linkedin.com/posts/iv%C3%A1n-castro-mart%C3%ADnez-293b9414a_ive-been-thinking-a-lot-about-the-future-activity-7217659492472107009--ifb",
    "description": "Future of Work",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7216163666256179202?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-05-04",
    "category": "Future of Work",
    "author": "me"
  },
  {
    "id": "li-tokii-vr-immersia",
    "url": "https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un",
    "description": "Tokii VR (Immersia)",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-05-04",
    "category": "AI/VR Education",
    "author": "me"
  },
  {
    "id": "li-neural-net-graphical",
    "url": "https://www.linkedin.com/posts/eric-vyacheslav-156273169_amazing-graphical-representation-of-a-neural-ugcPost-7274785920447320065-EPL4",
    "description": "Neural Net Graphical Representation",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7274785920447320065?collapsed=1" height="878" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2025-01-04",
    "category": "AI Visualization",
    "author": "recommended"
  },
  {
    "id": "li-immersia-visit",
    "url": "https://www.linkedin.com/posts/immersia-datavisualization_tokii-vr-tokii-ugcPost-7303414239958831104-x1Un",
    "description": "Japanese Delegation Visit",
    "embedCode": "<iframe src=\"https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7303414239958831104?collapsed=1\" height=\"543\" width=\"504\" frameborder=\"0\" allowfullscreen=\"\" title=\"Embedded post\"></iframe>",
    "publishedDate": "2025-04-27",
    "category": "Team/Culture",
    "author": "me"
  },
  {
    "id": "li-ai-glasses-privacy",
    "url": "https://www.linkedin.com/posts/endritrestelica_rip-privacy-this-guy-used-ai-powered-glasses-ugcPost-7320915912096657412-jeBW",
    "description": "AI Powered Glasses Privacy",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7320915912096657412?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2025-04-27",
    "category": "AI Privacy",
    "author": "recommended"
  },
  {
    "id": "li-visionarynet-ai",
    "url": "https://www.linkedin.com/posts/visionarynet_artificialintelligence-machinelearning-ml-ugcPost-7288501315444363264-lEa2",
    "description": "VisionaryNet AI",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7288501315444363264?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-04-10",
    "category": "Generative AI",
    "author": "recommended"
  },
   {
    "id": "li-smartglass-ai",
    "url": "https://www.linkedin.com/posts/smartglassnews_ai-tech-innovation-ugcPost-7170174855294730241-Bv4z",
    "description": "SmartGlass AI",
    "embedCode": '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7169728132965384192?collapsed=1" height="543" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    "publishedDate": "2024-02-25",
    "category": "Hardware/Devices",
    "author": "recommended"
   }
]

async def main():
    print("Starting LinkedIn posts migration script...")
    db: AsyncSession = AsyncSessionLocal()
    try:
        # 1. Find the first superuser
        stmt = select(User).filter(User.is_superuser == True).limit(1)
        result = await db.execute(stmt)
        superuser = result.scalars().first()

        if not superuser:
            print("Error: No superuser found. Assign a superuser before running the script.")
            print("You can do this directly in the database or through your application's logic.")
            return

        print(f"Superuser found: {superuser.email} (ID: {superuser.id})")

        migrated_count = 0
        skipped_count = 0
        placeholder_embed_code = "<!-- PASTE EMBED CODE HERE -->"

        for post_data in raw_linkedin_posts:
            if post_data["embedCode"] == placeholder_embed_code:
                print(f"Skipping post ID '{post_data['id']}' due to embed code placeholder.")
                skipped_count += 1
                continue
            
            # 2. Transform data
            title = post_data["description"]
            # Ensure the title is not excessively long for a slug
            if len(title) > 200:
                title = title[:200] + "..."
            
            content = post_data["description"] # Use description as main content
            excerpt = post_data["description"][:250] if len(post_data["description"]) > 250 else post_data["description"] # A longer excerpt
            
            tags = post_data["category"]
            linkedin_url = post_data["embedCode"] # This is the embed code
            
            # Convert publishedDate string to date object
            try:
                published_dt_obj = datetime.strptime(post_data["publishedDate"], "%Y-%m-%d").date()
            except ValueError:
                print(f"Error: Invalid date '{post_data['publishedDate']}' for post ID '{post_data['id']}'. Skipping this post.")
                skipped_count += 1
                continue

            blog_post_in = BlogPostCreate(
                title=title,
                content=content,
                excerpt=excerpt,
                tags=tags,
                image_url=None, # Embedded LinkedIn posts don't need a separate image
                linkedin_post_url=linkedin_url,
                status="published"
            )

            # 3. Check if a post with the same slug (generated from the title) already exists
            # The create_blog_post function already generates the slug.
            # However, for this script, it's good to check it BEFORE to avoid failing mid-process.
            # The crud create_blog_post function does NOT overwrite published_date, which is good here.
            
            temp_slug = slugify(blog_post_in.title)
            existing_post_by_slug = await get_blog_post_by_slug(db, slug=temp_slug)
            if existing_post_by_slug:
                print(f"Skipping post with title '{blog_post_in.title}' (slug: '{temp_slug}') because a post with that slug already exists.")
                skipped_count += 1
                continue

            # 4. Create and save the blog post
            # The `create_blog_post` function in crud_blog.py handles:
            # - Generating ID
            # - Generating Slug (we already checked this above, but the function will do it formally)
            # - Setting published_date (NOTE! We want to control this from the script)
            # - Setting author_id
            
            # We modify the call to create_blog_post to also pass the published_date
            # This requires us to adjust `crud.blog.create_blog_post` or create a version for the script.
            # For simplicity, we will create the BlogPost object directly here and add it.
            
            new_id = uuid.uuid4().hex # Import uuid
            
            db_blog_post = BlogPost(
                **blog_post_in.dict(exclude_unset=True), # Pass fields from BlogPostCreate
                id=new_id,
                slug=temp_slug, # We use the slug we already verified
                author_id=superuser.id,
                published_date=published_dt_obj # Use the publication date from the original post
                # last_modified_date will be updated automatically if configured in the model
            )
            
            db.add(db_blog_post)
            await db.commit()
            await db.refresh(db_blog_post)
            
            print(f"Post '{db_blog_post.title}' (ID: {db_blog_post.id}, Slug: {db_blog_post.slug}) created with publication date: {db_blog_post.published_date}")
            migrated_count += 1

    except Exception as e:
        print(f"An error occurred during migration: {e}")
        await db.rollback() # Ensure rollback in case of a general error
    finally:
        await db.close()
        await async_engine.dispose() # MODIFIED HERE

    print(f"--- Migration Summary ---")
    print(f"Posts migrated successfully: {migrated_count}")
    print(f"Posts skipped (placeholder, already existing, or date error): {skipped_count}")
    print("Migration script finished.")

if __name__ == "__main__":
    asyncio.run(main()) 