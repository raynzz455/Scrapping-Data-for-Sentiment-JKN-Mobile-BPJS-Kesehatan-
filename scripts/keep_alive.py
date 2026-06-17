"""
scripts/keep_alive.py
─────────────────────
Ping Supabase setiap 3 hari agar project tidak di-pause
(free tier pause setelah 7 hari tanpa aktivitas).

Cara pakai:
  1. Jalankan manual  : uv run python scripts/keep_alive.py
  2. GitHub Actions   : buat .github/workflows/keep_alive.yml
     (contoh di bawah)
  3. Cron lokal       : crontab -e
                        0 9 */3 * * cd /path/to/jkn-sentiment && uv run python scripts/keep_alive.py

GitHub Actions YAML:
─────────────────────────────────────────────────────────────
name: Keep Supabase Alive
on:
  schedule:
    - cron: '0 9 */3 * *'   # setiap 3 hari jam 9 pagi UTC
  workflow_dispatch:

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Ping Supabase
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          pip install supabase python-dotenv -q
          python scripts/keep_alive.py
─────────────────────────────────────────────────────────────
"""
import os
import sys
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


def ping():
    try:
        from supabase import create_client
    except ImportError:
        sys.exit("Jalankan: uv add supabase")

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        sys.exit("Set SUPABASE_URL dan SUPABASE_KEY di .env")

    db = create_client(url, key)

    # Query ringan: count reviews
    try:
        res = db.table("reviews").select("id", count="exact").limit(1).execute()
        count = res.count or 0
        print(f"[{datetime.now():%Y-%m-%d %H:%M}] ✓ Supabase aktif — {count} baris di tabel reviews")
    except Exception as e:
        print(f"[{datetime.now():%Y-%m-%d %H:%M}] ✗ Ping gagal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    ping()
