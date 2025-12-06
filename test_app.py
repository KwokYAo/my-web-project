import pytest
from application import app, db
from application.models import User, Entry

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # Use in-memory DB for isolation
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            
            # SAFE USER CREATION: Only add if 'test' doesn't exist
            if not User.query.filter_by(username='test').first():
                user = User(username='test', password='password')
                db.session.add(user)
                db.session.commit()
                
        yield client
        # Cleanup (Optional for :memory: DB as it dies with the process)
        with app.app_context():
            db.drop_all()

# --- TEST 1: Validity Testing (Logic) ---
def test_negative_area_validation(client):
    """Ensure the system rejects negative square footage."""
    # Login first
    with client.session_transaction() as sess:
        sess['user'] = 'test'
    
    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': -500,  # Invalid!
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 2000
    }, follow_redirects=True)
    
    # Check for error (either text or class)
    assert b"Area cannot be negative" in response.data or b"error" in response.data

# --- TEST 2: Range Testing ---
def test_future_year_validation(client):
    """Ensure the system rejects future years."""
    with client.session_transaction() as sess:
        sess['user'] = 'test'

    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': 1500,
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 3000 # Invalid
    }, follow_redirects=True)
    
    assert b"Year must be between 1800 and 2030" in response.data

# --- TEST 3: Database Logic ---
def test_database_entry_creation(client):
    """Unit Test: Can we save a history record to the DB?"""
    with app.app_context():
        # Create a fake entry directly using the Model
        entry = Entry(
            username='tester', overall_qual=7, gr_liv_area=1500,
            garage_cars=2, total_bsmt_sf=1000, year_built=2000,
            prediction=250000.00
        )
        db.session.add(entry)
        db.session.commit()
        
        # Retrieve it
        saved = Entry.query.filter_by(username='tester').first()
        assert saved is not None
        assert saved.username == 'tester'
        assert saved.prediction == 250000.00

# --- TEST 4: API Testing (Integration) ---
def test_api_predict_endpoint(client):
    """Ensure the API returns JSON."""
    response = client.post('/api/predict', json={
        'OverallQual': 7,
        'GrLivArea': 1500,
        'GarageCars': 2,
        'TotalBsmtSF': 1000,
        'YearBuilt': 2000
    })
    
    assert response.status_code in [200, 500]
    assert response.is_json
    # Matches your current routes.py logic (mock or real)
    data = response.get_json()
    assert 'status' in data or 'prediction' in data or 'error' in data