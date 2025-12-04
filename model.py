import pandas as pd
import joblib
import sqlite3
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# --- CONFIGURATION ---
DATA_FILE = 'AmesHousing_Cleaned.csv'  # Ensure this file is in your root folder
MODEL_FILE = 'housing_model.pkl'
DB_FILE = 'housing.db'

def train_model():
    print("--- 1. Loading Data ---")
    try:
        df = pd.read_csv(DATA_FILE)
        print(f"Loaded {len(df)} rows from {DATA_FILE}")
    except FileNotFoundError:
        print(f"ERROR: {DATA_FILE} not found. Please upload it!")
        return

    # --- FEATURE SELECTION ---
    # We use the 5 features we decided on + the Target (SalePrice)
    # Ensure these column names MATCH your CSV exactly!
    features = ['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt']
    target = 'SalePrice'

    # Check if columns exist
    missing_cols = [col for col in features + [target] if col not in df.columns]
    if missing_cols:
        print(f"ERROR: Missing columns in CSV: {missing_cols}")
        print("Available columns:", df.columns.tolist())
        return

    X = df[features]
    y = df[target]

    # --- TRAIN/TEST SPLIT ---
    print("--- 2. Training Model ---")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- MODEL TRAINING ---
    model = LinearRegression()
    model.fit(X_train, y_train)

    # --- EVALUATION ---
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

def setup_database():
    print("\n--- 4. Setting up Database ---")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE NOT NULL, 
                  password TEXT NOT NULL)''')

    # Create History Table (Matches our 5 features)
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  overall_qual INTEGER, 
                  gr_liv_area INTEGER, 
                  garage_cars INTEGER, 
                  total_bsmt_sf INTEGER, 
                  year_built INTEGER,  
                  prediction REAL, 
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Default Admin User
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'password'))
        print("Created default user: admin / password")
    except sqlite3.IntegrityError:
        print("User 'admin' already exists.")

    conn.commit()
    conn.close()
    print(f"SUCCESS: Database {DB_FILE} is ready.")

if __name__ == "__main__":
    train_model()
    setup_database()