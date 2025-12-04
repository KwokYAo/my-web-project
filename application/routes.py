from application import app
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from application.forms import PredictionForm, LoginForm
import sqlite3
import joblib
import pandas as pd

# Load Model
try:
    model = joblib.load('housing_model.pkl')
except:
    model = None

def get_db():
    conn = sqlite3.connect('housing.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # --- FIXED LOGIN LOGIC (From your fix branch) ---
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
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session: return redirect(url_for('login'))
    
    form = PredictionForm()
    prediction_text = None
    
    # --- FIXED PREDICT LOGIC (From your feature branch) ---
    if request.method == 'POST':
        if form.validate_on_submit():
            # Clean Data from Form
            qual = form.overall_qual.data
            area = form.gr_liv_area.data
            cars = form.garage_cars.data
            bsmt = form.total_bsmt_sf.data
            year = form.year_built.data
            
            # --- MOCK PREDICTION FORMULA (For Visual Testing) ---
            pred_value = (qual * 15000) + (area * 75) + (cars * 5000) + (bsmt * 50) + (year * 10)
            prediction_text = f"{pred_value:,.2f}"
            
            flash(f"Success! Estimated Value: ${prediction_text}", "success")
        else:
            flash("Error, cannot proceed with prediction", "danger")

    return render_template('predict.html', form=form, prediction=prediction_text)

@app.route('/history')
def history():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db()
    try:
        rows = conn.execute('SELECT * FROM history WHERE username = ? ORDER BY timestamp DESC', (session['user'],)).fetchall()
        conn.close()
        return render_template('history.html', history=rows)
    except:
        return render_template('history.html', history=[])

@app.route('/delete_history/<int:id>')
def delete_history(id):
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db()
    conn.execute('DELETE FROM history WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Record deleted.", "info")
    return redirect(url_for('history'))

# --- API ROUTE (Placeholder) ---
@app.route('/api/predict', methods=['POST'])
def api_predict():
    if request.is_json:
        data = request.get_json()
        try:
            qual = int(data.get('OverallQual'))
            # ... (rest of logic) ...
            return jsonify({'prediction': 150000, 'status': 'success (mock)'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    return jsonify({'error': 'Request must be JSON'}), 415