import pytest
import pandas as pd
import joblib
import os

# --- TEST 1: Existence Check ---
def test_model_file_exists():
    """
    Test that the trained model file actually exists on disk.
    If this fails, the app will 100% crash.
    """
    assert os.path.exists('housing_model.pkl')

# --- TEST 2: Loading Check ---
def test_model_loading():
    """
    Test that we can load the model without errors using joblib.
    """
    try:
        model = joblib.load('housing_model.pkl')
    except Exception as e:
        pytest.fail(f"Failed to load model: {e}")
    
    # Ensure it's the right type (sklearn object)
    assert hasattr(model, 'predict')

# --- TEST 3: Prediction Consistency ---
def test_prediction_shape_and_type():
    """
    Test that the model accepts the EXACT 5 features we expect
    and returns a float value (price).
    """
    model = joblib.load('housing_model.pkl')
    
    # Create a dummy input dataframe with the 5 specific columns
    # Order matters!
    input_data = pd.DataFrame([[5, 1500, 2, 800, 1995]], 
                              columns=['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt'])
    
    prediction = model.predict(input_data)
    
    # Check result
    assert len(prediction) == 1
    assert isinstance(prediction[0], float)
    assert prediction[0] > 0  # Price should be positive