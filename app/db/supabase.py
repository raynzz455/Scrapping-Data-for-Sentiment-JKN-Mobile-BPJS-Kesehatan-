"""
Supabase client — singleton connection untuk seluruh app.
"""
import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def get_supabase() -> Client:
    url  = os.getenv("SUPABASE_URL")
    key  = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise EnvironmentError(
            "SUPABASE_URL dan SUPABASE_KEY harus diset di .env"
        )
    return create_client(url, key)


def get_db() -> Client:
    """FastAPI dependency — inject Supabase client."""
    return get_supabase()
