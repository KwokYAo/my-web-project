from application import app
from flask import render_template, request, redirect, url_for, session, flash ,jsonify
from application.form import PredictionForm
import pandas as pd 
# --- ROUTES ---

@app.route('/hello')
def hello_world():
    return "<h1>Hello Ames Housing AI</h1>"

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template("index.html", title="Welcome to Ames AI")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Mock Login for Visual Testing
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if password == 'password':
            session['user'] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('predict'))
        else:
            flash("Invalid Credentials (Try password: 'password')", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# --- PREDICT ROUTE (Adapted from Iris Example) ---
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session: return redirect(url_for('login'))
    
    # 1. Initialize the Form
    form = PredictionForm()
    prediction_text = None
    
    # 2. Handle POST Request
    if request.method == 'POST':
        
        # 3. Check Validation (WTF Logic)
        if form.validate_on_submit():
            # Extraction (Clean data from WTF)
            qual = form.overall_qual.data
            area = form.gr_liv_area.data
            cars = form.garage_cars.data
            bsmt = form.total_bsmt_sf.data
            year = form.year_built.data
            
            # --- MOCK PREDICTION (Since model is not loaded) ---
            # We just calculate a dummy number to prove the flow works
            dummy_result = (qual * 5000) + (area * 100) + (year * 10)
            prediction_text = f"{dummy_result:,.2f}"
            
            flash(f"Success! Form Validated. Mock Price: ${prediction_text}", "success")
            
            # (Note: Database saving is removed as requested)
            
        else:
            # 4. Handle Failure
            # If validators fail (e.g., negative area), this runs.
            # Errors are automatically sent to the form object.
            flash("Error: Cannot proceed with prediction. Check fields below.", "danger")

    # 5. Render Template
    # Crucial: Pass 'form=form' so the HTML can show the red error messages
    return render_template('predict.html', 
                           title="Predict House Price", 
                           form=form, 
                           prediction=prediction_text)

# (History routes temporarily removed or mocked if needed)
@app.route('/history')
def history():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('history.html', history=[]) # Empty list for now


@app.route('/api/predict', methods=['POST'])
def api_predict():
    # 1. Check if the request is JSON (Machine talk), not a Form (Human talk)
    if request.is_json:
        data = request.get_json()
        
        # 2. Extract data safely
        try:
            qual = int(data.get('OverallQual'))
            area = int(data.get('GrLivArea'))
            cars = int(data.get('GarageCars'))
            bsmt = int(data.get('TotalBsmtSF'))
            year = int(data.get('YearBuilt'))
            
            input_df = pd.DataFrame([[qual, area, cars, bsmt, year]], 
                                    columns=['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt'])
            
            if model:
                prediction = model.predict(input_df)[0]
                return jsonify({'prediction': prediction, 'status': 'success'}), 200
            else:
                return jsonify({'error': 'Model not loaded'}), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
            
    return jsonify({'error': 'Request must be JSON'}), 415