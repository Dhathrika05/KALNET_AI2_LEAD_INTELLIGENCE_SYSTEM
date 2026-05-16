from .config import Config
from sqlalchemy import create_engine


def get_engine():

    try:

        engine = create_engine(
            Config.DATABASE_URL
        )

        print("Connected to Neon PostgreSQL successfully.")

        return engine

    except Exception as e:

        print(f"Engine creation failed: {e}")

        return None