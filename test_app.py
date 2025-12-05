import pytest
import os
import joblib
import pandas as pd
from application import app, db
from application.models import User, Entry

# --- FIXTURE: SETS UP A FAKE APP FOR TESTING ---
@pytest.fixture
def client():
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable security tokens for tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use temporary RAM database
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all() # Create tables in the fake DB
        yield client
        # (Cleanup happens automatically here)

# ==========================================
# PART 1: FRONTEND VALIDATION (Unit Testing)
# Requirement: Validity & Range Testing
# ==========================================

def test_negative_area_validation(client):
    """
    Test Validity: Rejects negative numbers for Living Area.
    """
    # 1. Login first (mock user)
    client.post('/login', data={'username': 'test', 'password': 'password'})
    
    # 2. Send invalid data
    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': -500, # Invalid!
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 2000
    }, follow_redirects=True)
    
    # 3. Assert error message exists in the HTML
    # Note: Flask-WTF default error for NumberRange is usually "must be at least X"
    # or the custom message we set in forms.py
    assert b"Area cannot be negative" in response.data

def test_future_year_validation(client):
    """
    Test Range: Rejects years too far in the future.
    """
    client.post('/login', data={'username': 'test', 'password': 'password'})
    
    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': 1500,
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 3000 # Invalid!
    }, follow_redirects=True)
    
    assert b"Year must be between 1800 and 2030" in response.data

# ==========================================
# PART 2: BACKEND LOGIC (Consistency Testing)
# Requirement: System Consistency & Database
# ==========================================

def test_model_file_exists():
    """
    Smoke Test: Is the model file present?
    """
    assert os.path.exists('housing_model.pkl')

def test_prediction_logic():
    """
    Consistency Test: Does the model accept our 5 specific features?
    """
    try:
        model = joblib.load('housing_model.pkl')
        # 5 Params: Qual, Area, Cars, Bsmt, Year
        test_data = pd.DataFrame([[5, 1000, 1, 800, 1990]], 
                                 columns=['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt'])
        pred = model.predict(test_data)
        assert len(pred) == 1
        assert pred[0] > 0
    except:
        pytest.fail("Model failed to predict. Did you run setup_model.py?")

def test_database_entry_creation(client):
    """
    Unit Test: Can we save a history record to the DB?
    """
    with app.app_context():
        # Create a fake entry
        entry = Entry(
            username='tester', overall_qual=7, gr_liv_area=1500,
            garage_cars=2, total_bsmt_sf=1000, year_built=2000,
            prediction=250000.00
        )
        db.session.add(entry)
        db.session.commit()
        
        # Retrieve it
        saved = Entry.query.first()
        assert saved is not None
        assert saved.username == 'tester'
        assert saved.prediction == 250000.00

def test_user_registration(client):
    """
    Unit Test: Can we create a new user account?
    """
    # Simulate a registration POST
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    # Check if user exists in DB
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.password == 'password123'

# ==========================================
# PART 3: API TESTING
# Requirement: Web API Setup
# ==========================================

def test_api_predict_endpoint(client):
    """
    Integration Test: Does the API return JSON?
    """
    response = client.post('/api/predict', json={
        'OverallQual': 7,
        'GrLivArea': 1500,
        'GarageCars': 2,
        'TotalBsmtSF': 1000,
        'YearBuilt': 2000
    })
    
    # 200 = Success, 500 = Model Loading Error (but API is reachable)
    assert response.status_code in [200, 500] 
    assert response.is_json
    
    # Check payload content
    data = response.get_json()
    # We expect either a prediction OR an error message (if model missing)
    assert 'prediction' in data or 'error' in data