import asyncio

from dotenv import load_dotenv

from .server import run_server

load_dotenv()


def startup():
    print("starting startup...")

    run_server(host="0.0.0.0", port=8008)
    
    print("finalizing startup.")

if __name__ == "__main__":
    asyncio.run(startup())
