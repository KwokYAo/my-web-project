import pytest
from application import app, db
# [FIX] Changed 'Entry' to 'History'
from application.models import User, History 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for easier testing
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_register(client):
    """Test that registration works"""
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)
    assert b"Account created" in response.data

def test_login(client):
    """Test that login works"""
    # Create user first
    client.post('/register', data={
        'username': 'testuser',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)

    # Try login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert b"Welcome back" in response.data

def test_add_prediction(client):
    """Test that a prediction is saved to History"""
    # 1. Login
    client.post('/register', data={
        'username': 'testuser',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)
    client.post('/login', data={'username': 'testuser', 'password': 'password'}, follow_redirects=True)

    # 2. Make Prediction
    response = client.post('/predict', data={
        'overall_qual': 7,
        'gr_liv_area': 1500,
        'garage_cars': 2,
        'total_bsmt_sf': 1000,
        'year_built': 2000
    }, follow_redirects=True)

    # 3. Check Database (Using 'History', not 'Entry')
    assert b"Success! Estimated Value" in response.data
    with app.app_context():
        assert History.query.count() == 1
        assert History.query.first().overall_qual == 7

def test_update_account(client):
    """Test that a user can change their username"""
    # 1. Login
    client.post('/register', data={
        'username': 'OldName',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)
    client.post('/login', data={'username': 'OldName', 'password': 'password'}, follow_redirects=True)

    # 2. Change Name
    response = client.post('/account', data={
        'username': 'NewName',
        'password': '',
        'confirm_password': ''
    }, follow_redirects=True)

    # 3. Verify
    assert b"Your account has been updated" in response.data
    with app.app_context():
        user = User.query.first()
        assert user.username == 'NewName'

def test_delete_account(client):
    """Test account deletion"""
    # 1. Login
    client.post('/register', data={
        'username': 'DeleteMe',
        'password': 'password',
        'confirm_password': 'password'
    }, follow_redirects=True)
    client.post('/login', data={'username': 'DeleteMe', 'password': 'password'}, follow_redirects=True)

    # 2. Delete
    response = client.post('/account/delete', follow_redirects=True)
    assert b"Your account has been deleted" in response.data

    # 3. Verify user is gone
    with app.app_context():
        assert User.query.count() == 0