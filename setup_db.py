import psycopg2
from config import HOST, PORT, DBNAME, USER, PASSWORD

conn = psycopg2.connect(
    host=HOST, port=PORT, dbname=DBNAME,
    user=USER, password=PASSWORD, sslmode="require"
)
cur = conn.cursor()

# Create users table
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id            SERIAL PRIMARY KEY,
        email         VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

# Create transactions table
cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id          SERIAL PRIMARY KEY,
        user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
        type        VARCHAR(10)     NOT NULL CHECK (type IN ('income', 'expense')),
        amount      DECIMAL(10,2)   NOT NULL CHECK (amount > 0),
        category    VARCHAR(100)    NOT NULL,
        description TEXT,
        date        DATE            DEFAULT CURRENT_DATE,
        created_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP
    );
""")

conn.commit()
cur.close()
conn.close()
print("✅ Users and Transactions tables created successfully!")