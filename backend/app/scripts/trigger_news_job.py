import asyncio
from app.main import run_fetch_news_job

async def main():
    print("--- MANUALLY TRIGGERING NEWS FETCH JOB ---")
    await run_fetch_news_job()
    print("--- JOB EXECUTION FINISHED ---")

if __name__ == "__main__":
    asyncio.run(main()) 