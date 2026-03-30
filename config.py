import os

HOST       = os.environ.get("DB_HOST", "nvy0kyrux9.ss0agn1k1t.tsdb.cloud.timescale.com")
PORT       = int(os.environ.get("DB_PORT", "39045"))
DBNAME     = os.environ.get("DB_NAME", "tsdb")
USER       = os.environ.get("DB_USER", "tsdbadmin")
PASSWORD   = os.environ.get("DB_PASSWORD", "GABRUJAWAN@92666")
JWT_SECRET = os.environ.get("JWT_SECRET", "zorvyn-finance-secret-key-2026-secure")