import os

HOST       = os.environ.get("HOST", "nvy0kyrux9.ss0agn1k1t.tsdb.cloud.timescale.com")
PORT       = int(os.environ.get("PORT", "39045"))
DBNAME     = os.environ.get("DBNAME", "tsdb")
USER       = os.environ.get("USER", "tsdbadmin")
PASSWORD   = os.environ.get("PASSWORD", "GABRUJAWAN@92666")
JWT_SECRET = os.environ.get("JWT_SECRET", "zorvyn-finance-secret-key-2026-secure")