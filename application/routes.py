from application import app
from flask import render_template, request, redirect, url_for, session, flash
from application.form import PredictionForm, LoginForm 

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
    if 'user' in session:
        return redirect(url_for('predict'))

    form = LoginForm()
    
    # WTF Logic: This handles POST check + Validation automatically
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # MOCK LOGIN LOGIC (Replace with DB logic later if needed)
        if password == 'password':
            session['user'] = username
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for('predict'))
        else:
            flash("Invalid Credentials (Try password: 'password')", "danger")
            
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('login'))

# --- PREDICT ROUTE (Adapted from Iris Example) ---
@app.route('/predict', methods=['GET', 'POST'])
def predict():
   # if 'user' not in session: return redirect(url_for('login'))
    
    # 1. Initialize the Form
    form = PredictionForm()
    prediction_text = None
    
    # 2. Handle POST Request & Validation
    if form.validate_on_submit():
        # --- SUCCESS BLOCK ---
        # If we are here, ALL inputs are valid (including Garage=0).
        
        # Extraction (Clean data from WTF)
        qual = form.overall_qual.data
        area = form.gr_liv_area.data
        cars = form.garage_cars.data
        bsmt = form.total_bsmt_sf.data
        year = form.year_built.data
        
        # --- MOCK PREDICTION (Replace with real model later) ---
        dummy_result = (qual * 5000) + (area * 100) + (cars * 2000) + (year * 10)
        prediction_text = f"{dummy_result:,.2f}"
        
        flash(f"Success! Prediction calculated: ${prediction_text}", "success")
        
    elif request.method == 'POST':
        # --- FAILURE BLOCK ---
        # If validation failed, Flask-WTF adds errors to form.errors
        # We just flash a generic message. The specific errors show up in HTML.
        flash("Error: Please fix the issues in the form below.", "danger")

    # 5. Render Template
    return render_template('predict.html', 
                           title="Predict House Price", 
                           form=form, 
                           prediction=prediction_text)

# (History routes temporarily removed or mocked if needed)
@app.route('/history')
def history():
   # if 'user' not in session: return redirect(url_for('login'))
    return render_template('history.html', history=[]) # Empty list for now