from flask import Flask, request, jsonify
from db import get_connection
from auth import hash_password, check_password, generate_token, verify_token
from datetime import datetime, timezone

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "name": "Personal Finance Tracker API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health":   "GET  /health",
            "register": "POST /register",
            "login":    "POST /login",
            "transactions": {
                "add":     "POST   /transactions",
                "get_all": "GET    /transactions",
                "summary": "GET    /transactions/summary",
                "delete":  "DELETE /transactions/<id>"
            }
        },
        "docs": "github.com/dhruvkumargrow-cyber/personal-finance-tracker"
    }), 200

# ── Helper — extract user from token ──────────────────
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    return verify_token(token)

# ── Health check ───────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

# ── Register ───────────────────────────────────────────
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    email    = data['email'].lower().strip()
    password = data['password']

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"error": "Email already registered"}), 409

    password_hash = hash_password(password)
    cur.execute("""
        INSERT INTO users (email, password_hash)
        VALUES (%s, %s)
        RETURNING id, email, created_at;
    """, (email, password_hash))

    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Account created successfully",
        "user": {
            "id":    row[0],
            "email": row[1]
        }
    }), 201

# ── Login ──────────────────────────────────────────────
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    email    = data['email'].lower().strip()
    password = data['password']

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE email = %s;", (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row or not check_password(password, row[1]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(row[0])
    return jsonify({
        "message": "Login successful",
        "token":   token
    }), 200

# ── Add transaction ────────────────────────────────────
@app.route('/transactions', methods=['POST'])
def add_transaction():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized — please login"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    type_       = data.get('type')
    amount      = data.get('amount')
    category    = data.get('category')
    description = data.get('description', '')
    date        = data.get('date')

    if not type_ or not amount or not category:
        return jsonify({"error": "type, amount and category are required"}), 400

    if type_ not in ['income', 'expense']:
        return jsonify({"error": "type must be income or expense"}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except ValueError:
        return jsonify({"error": "amount must be a positive number"}), 400

    conn = get_connection()
    cur  = conn.cursor()

    if date:
        cur.execute("""
            INSERT INTO transactions
            (user_id, type, amount, category, description, date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, type, amount, category, description, date, created_at;
        """, (user_id, type_, amount, category, description, date))
    else:
        cur.execute("""
            INSERT INTO transactions
            (user_id, type, amount, category, description)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, type, amount, category, description, date, created_at;
        """, (user_id, type_, amount, category, description))

    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id":          row[0],
        "type":        row[1],
        "amount":      float(row[2]),
        "category":    row[3],
        "description": row[4],
        "date":        str(row[5]),
        "created_at":  str(row[6])
    }), 201

# ── Get all transactions ───────────────────────────────
@app.route('/transactions', methods=['GET'])
def get_transactions():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized — please login"}), 401

    type_    = request.args.get('type')
    category = request.args.get('category')

    query  = """
        SELECT id, type, amount, category, description, date, created_at
        FROM transactions
        WHERE user_id = %s
    """
    params = [user_id]

    if type_:
        query += " AND type = %s"
        params.append(type_)
    if category:
        query += " AND category = %s"
        params.append(category)

    query += " ORDER BY date DESC, created_at DESC;"

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    transactions = [{
        "id":          row[0],
        "type":        row[1],
        "amount":      float(row[2]),
        "category":    row[3],
        "description": row[4],
        "date":        str(row[5]),
        "created_at":  str(row[6])
    } for row in rows]

    return jsonify(transactions), 200

# ── Monthly summary ────────────────────────────────────
@app.route('/transactions/summary', methods=['GET'])
def get_summary():
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized — please login"}), 401

    month = request.args.get('month', datetime.now(timezone.utc).strftime('%Y-%m'))

    try:
        year, mon = month.split('-')
        year = int(year)
        mon  = int(mon)
    except ValueError:
        return jsonify({"error": "month must be in YYYY-MM format"}), 400

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT
            COALESCE(SUM(CASE WHEN type = 'income'  THEN amount ELSE 0 END), 0) AS total_income,
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) AS total_expenses,
            COUNT(*) AS transaction_count
        FROM transactions
        WHERE user_id = %s
          AND EXTRACT(YEAR  FROM date) = %s
          AND EXTRACT(MONTH FROM date) = %s;
    """, (user_id, year, mon))

    row = cur.fetchone()

    cur.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE user_id = %s
          AND type = 'expense'
          AND EXTRACT(YEAR  FROM date) = %s
          AND EXTRACT(MONTH FROM date) = %s
        GROUP BY category
        ORDER BY total DESC;
    """, (user_id, year, mon))

    categories = cur.fetchall()
    cur.close()
    conn.close()

    total_income   = float(row[0])
    total_expenses = float(row[1])
    savings        = total_income - total_expenses

    return jsonify({
        "month":               month,
        "total_income":        total_income,
        "total_expenses":      total_expenses,
        "savings":             savings,
        "transaction_count":   row[2],
        "top_expense_categories": [
            {"category": r[0], "total": float(r[1])}
            for r in categories
        ]
    }), 200

# ── Delete transaction ─────────────────────────────────
@app.route('/transactions/<int:txn_id>', methods=['DELETE'])
def delete_transaction(txn_id):
    user_id = get_current_user()
    if not user_id:
        return jsonify({"error": "Unauthorized — please login"}), 401

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT id FROM transactions
        WHERE id = %s AND user_id = %s;
    """, (txn_id, user_id))

    if not cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"error": "Transaction not found"}), 404

    cur.execute("DELETE FROM transactions WHERE id = %s;", (txn_id,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Transaction deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)