import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def get_token(client):
    client.post('/register',
        data=json.dumps({
            "email": "test@finance.com",
            "password": "test1234"
        }),
        content_type='application/json'
    )
    response = client.post('/login',
        data=json.dumps({
            "email": "test@finance.com",
            "password": "test1234"
        }),
        content_type='application/json'
    )
    return response.get_json().get('token')

# ── Health check ───────────────────────────────────────
def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'

# ── Register tests ─────────────────────────────────────
def test_register_success(client):
    import time
    unique_email = f"newuser{int(time.time())}@test.com"
    response = client.post('/register',
        data=json.dumps({
            "email": unique_email,
            "password": "password123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 201
    assert 'user' in response.get_json()

    
def test_register_missing_email(client):
    response = client.post('/register',
        data=json.dumps({"password": "password123"}),
        content_type='application/json'
    )
    assert response.status_code == 400

def test_register_short_password(client):
    response = client.post('/register',
        data=json.dumps({
            "email": "short@test.com",
            "password": "abc"
        }),
        content_type='application/json'
    )
    assert response.status_code == 400

# ── Login tests ────────────────────────────────────────
def test_login_success(client):
    client.post('/register',
        data=json.dumps({
            "email": "login@test.com",
            "password": "password123"
        }),
        content_type='application/json'
    )
    response = client.post('/login',
        data=json.dumps({
            "email": "login@test.com",
            "password": "password123"
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert 'token' in response.get_json()

def test_login_wrong_password(client):
    client.post('/register',
        data=json.dumps({
            "email": "wrong@test.com",
            "password": "correct123"
        }),
        content_type='application/json'
    )
    response = client.post('/login',
        data=json.dumps({
            "email": "wrong@test.com",
            "password": "wrongpassword"
        }),
        content_type='application/json'
    )
    assert response.status_code == 401

# ── Transaction tests ──────────────────────────────────
def test_add_income(client):
    token = get_token(client)
    response = client.post('/transactions',
        data=json.dumps({
            "type": "income",
            "amount": 50000,
            "category": "Salary"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.get_json()['type'] == 'income'

def test_add_expense(client):
    token = get_token(client)
    response = client.post('/transactions',
        data=json.dumps({
            "type": "expense",
            "amount": 5000,
            "category": "Food"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.get_json()['type'] == 'expense'

def test_add_transaction_invalid_type(client):
    token = get_token(client)
    response = client.post('/transactions',
        data=json.dumps({
            "type": "invalid",
            "amount": 5000,
            "category": "Food"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_add_transaction_no_auth(client):
    response = client.post('/transactions',
        data=json.dumps({
            "type": "income",
            "amount": 5000,
            "category": "Salary"
        }),
        content_type='application/json'
    )
    assert response.status_code == 401

def test_get_transactions(client):
    token = get_token(client)
    response = client.get('/transactions',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_get_transactions_no_auth(client):
    response = client.get('/transactions')
    assert response.status_code == 401

def test_get_summary(client):
    token = get_token(client)
    response = client.get('/transactions/summary',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert 'total_income' in data
    assert 'total_expenses' in data
    assert 'savings' in data

def test_delete_transaction(client):
    token = get_token(client)
    create = client.post('/transactions',
        data=json.dumps({
            "type": "expense",
            "amount": 1000,
            "category": "Test"
        }),
        content_type='application/json',
        headers={"Authorization": f"Bearer {token}"}
    )
    txn_id = create.get_json()['id']
    response = client.delete(f'/transactions/{txn_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

def test_delete_nonexistent_transaction(client):
    token = get_token(client)
    response = client.delete('/transactions/999999',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404