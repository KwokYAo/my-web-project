import pytest
import pandas as pd
import joblib
import os
from application import app, db
from application.models import Entry

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
# TEST GROUP 1: LOGIN LOGIC
# ==========================================
def test_login_page_loads(client):
    """Check if the login page actually exists."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_logic(client):
    """Check if we can log in with the mock password."""
    response = client.post('/login', data={
        'username': 'test_user',
        'password': 'password'
    }, follow_redirects=True)
    
    # Expect success message or redirect to dashboard
    assert b"Welcome back" in response.data or b"Dashboard" in response.data

# ==========================================
# TEST GROUP 2: AI MODEL INTEGRATION
# ==========================================
def test_model_file_exists():
    """Check if the brain (.pkl file) is present."""
    assert os.path.exists('housing_model.pkl')

def test_prediction_logic():
    """Check if the model accepts our 5 specific features."""
    try:
        model = joblib.load('housing_model.pkl')
        # 5 Params: Qual, Area, Cars, Bsmt, Year
        test_data = pd.DataFrame([[5, 1000, 1, 800, 1990]], 
                                 columns=['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt'])
        pred = model.predict(test_data)
        assert pred[0] > 0
    except:
        pytest.fail("Model failed to predict. Did you run setup_model.py?")

# ==========================================
# TEST GROUP 3: DATABASE LOGIC
# ==========================================
def test_database_save(client):
    """Check if we can save a history record."""
    with app.app_context():
        # Create a fake entry
        entry = Entry(
            username='tester', overall_qual=5, gr_liv_area=1000, 
            garage_cars=1, total_bsmt_sf=800, year_built=1990, 
            prediction=150000.0
        )
        db.session.add(entry)
        db.session.commit()

        # Retrieve it
        saved = Entry.query.first()
        assert saved is not None
        assert saved.username == 'tester'