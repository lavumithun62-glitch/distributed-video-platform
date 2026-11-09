import asyncio
import logging

from backend.transcoding_worker.app.worker import run_worker

logging.basicConfig(level=logging.INFO)


async def main():
    await run_worker()


if __name__ == "__main__":
    asyncio.run(main())