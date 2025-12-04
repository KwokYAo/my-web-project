import pytest
from application import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user'] = 'test_user'
        yield client

# --- TEST 1: Validity Testing (Negative Area) ---
def test_negative_area_rejection(client):
    """
    Test that entering a negative Living Area triggers a validation error.
    Requirement: Validity Testing
    """
    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': -100,  # Invalid!
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 2000
    }, follow_redirects=True)
    
    # Check if the error message from forms.py appears in the HTML
    assert b"Area cannot be negative" in response.data

# --- TEST 2: Range Testing (Year in Future) ---
def test_future_year_rejection(client):
    """
    Test that entering a year > 2030 triggers a validation error.
    Requirement: Range Testing
    """
    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': 1500,
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 3000  # Invalid!
    }, follow_redirects=True)
    
    assert b"Year must be between 1900 and 2030" in response.data

# --- TEST 3: Consistency/Happy Path ---
def test_valid_prediction(client):
    """
    Test that valid inputs result in a successful prediction (Green flash message).
    """
    response = client.post('/predict', data={
        'overall_qual': 5,
        'gr_liv_area': 1500,
        'garage_cars': 2,
        'total_bsmt_sf': 800,
        'year_built': 2000
    }, follow_redirects=True)
    
    assert b"Success!" in response.data