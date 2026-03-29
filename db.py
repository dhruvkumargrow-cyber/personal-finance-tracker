import psycopg2
from config import HOST, PORT, DBNAME, USER, PASSWORD

def get_connection():
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        user=USER,
        password=PASSWORD,
        sslmode="require"
    )