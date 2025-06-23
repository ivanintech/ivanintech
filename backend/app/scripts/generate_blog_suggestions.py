# import asyncio
# import logging
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
#
# from app.db.session import AsyncSessionLocal
# from app.services.gemini_service import GeminiService
# from app import crud
# from app.schemas.blog_suggestion import BlogSuggestionCreate
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# async def generate_suggestions():
#     """
#     Main function to generate and store new blog post suggestions.
#     """
#     logger.info("Starting blog suggestion generation process...")
#     # ... (toda la lógica comentada)
#
# async def main():
#     # await generate_suggestions()
#     logger.info("Generation script is currently disabled.")
#
# if __name__ == "__main__":
#     # asyncio.run(main())
#     pass 