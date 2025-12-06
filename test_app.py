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

def test_history_filter_and_sort(client):
    """Test that we can filter by Quality and Sort by Price"""
    # 1. Login
    client.post('/register', data={'username': 'SortUser', 'password': 'pw', 'confirm_password': 'pw'}, follow_redirects=True)
    client.post('/login', data={'username': 'SortUser', 'password': 'pw'}, follow_redirects=True)

    # 2. Manually add 3 History entries to DB (So we control the exact prices)
    from application.models import History, User
    from datetime import datetime
    
    with app.app_context():
        user = User.query.filter_by(username='SortUser').first()
        
        # House A: Cheap, Low Quality
        h1 = History(overall_qual=5, gr_liv_area=1000, garage_cars=1, total_bsmt_sf=800, year_built=1990, 
                     prediction=100000.0, predicted_on=datetime(2023, 1, 1), author=user)
        
        # House B: Expensive, Low Quality
        h2 = History(overall_qual=5, gr_liv_area=2000, garage_cars=2, total_bsmt_sf=1200, year_built=2000, 
                     prediction=500000.0, predicted_on=datetime(2023, 1, 2), author=user)
        
        # House C: Medium, High Quality
        h3 = History(overall_qual=9, gr_liv_area=1500, garage_cars=2, total_bsmt_sf=1000, year_built=2010, 
                     prediction=300000.0, predicted_on=datetime(2023, 1, 3), author=user)
        
        db.session.add_all([h1, h2, h3])
        db.session.commit()

    # 3. TEST FILTER: Ask only for Quality = 9
    # Should see House C ($300k), but NOT House A ($100k)
    response = client.get('/history?quality=9', follow_redirects=True)
    assert b"300,000.00" in response.data
    assert b"100,000.00" not in response.data

    # 4. TEST SORT: Ask for Price High-to-Low
    # Should see $500k (House B) appearing BEFORE $100k (House A)
    response = client.get('/history?sort=price&order=desc', follow_redirects=True)
    html = response.data.decode('utf-8')
    
    # Check positions in text
    pos_expensive = html.find("500,000.00")
    pos_cheap = html.find("100,000.00")
    
    assert pos_expensive < pos_cheap  # Expensive must be first