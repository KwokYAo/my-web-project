import pandas as pd
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# --- CONFIGURATION ---
DATA_FILE = 'AmesHousing_Cleaned.csv'
MODEL_FILE = 'housing_model.pkl'

def train_model():
    print("--- 1. Loading Data ---")
    try:
        df = pd.read_csv(DATA_FILE)
        print(f"Loaded {len(df)} rows from {DATA_FILE}")
    except FileNotFoundError:
        print(f"ERROR: {DATA_FILE} not found. Please upload it!")
        return

    # --- FEATURE SELECTION ---
    # The 5 features + Target
    features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt']
    target = 'SalePrice'

    # Check for missing columns to prevent crashes
    missing_cols = [col for col in features + [target] if col not in df.columns]
    if missing_cols:
        print(f"ERROR: Missing columns in CSV: {missing_cols}")
        return

    X = df[features]
    y = df[target]

    # --- TRAIN/TEST SPLIT ---
    print("--- 2. Training Model ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- MODEL TRAINING ---
    model = LinearRegression()
    model.fit(X_train, y_train)

    # --- EVALUATION (Just for your info) ---
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"Model Performance:")
    print(f"  MAE: ${mae:,.2f}")
    print(f"  R2 Score: {r2:.4f}")

    # --- SAVE MODEL ---
    print("--- 3. Saving Model ---")
    joblib.dump(model, MODEL_FILE)
    print(f"SUCCESS: Model saved to {MODEL_FILE}")

if __name__ == "__main__":
    train_model()