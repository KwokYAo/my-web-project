from application import app, db
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from application.form import PredictionForm, LoginForm,RegisterForm
from application.models import Entry,User
from datetime import datetime
import pandas as pd
import joblib


try:
    model = joblib.load('housing_model.pkl')
except:
    model = None

def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as error:
        db.session.rollback()
        flash(error, "danger")
        return 0

def get_entries():
    try:
        # Fetch entries only for the logged-in user
        if 'user' in session:
            entries = Entry.query.filter_by(username=session['user']).order_by(Entry.predicted_on.desc()).all()
            return entries
        return []
    except Exception as error:
        db.session.rollback()
        flash(error, "danger")
        return []

def remove_entry(id):
    try:
        entry = Entry.query.get(id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            flash("Record deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash(error, "danger")

# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Create new user
            new_user = User(username=form.username.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
            
            flash(f"Account created for {form.username.data}! Please login.", "success")
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
            
    return render_template('register.html', form=form)

# 2. UPDATED LOGIN ROUTE (Connects to DB)
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        # Query the Database
        user = User.query.filter_by(username=username).first()

        # Check if user exists AND password matches
        if user and user.password == password:
            session['user'] = user.username
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('predict'))
        else:
            flash("Invalid Username or Password", "danger")
            
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
    
    if form.validate_on_submit():
        # 1. Get Data
        qual = form.overall_qual.data
        area = form.gr_liv_area.data
        cars = form.garage_cars.data
        bsmt = form.total_bsmt_sf.data
        year = form.year_built.data
        
        # 2. Predict
        input_df = pd.DataFrame([[qual, area, cars, bsmt, year]], 
                                columns=['OverallQual', 'GrLivArea', 'GarageCars', 'TotalBsmtSF', 'YearBuilt'])
        
        if model:
            pred_value = model.predict(input_df)[0]
            prediction_text = f"{pred_value:,.2f}"
            
            # 3. SAVE TO DB (Using SQLAlchemy Model)
            new_entry = Entry(
                username=session['user'],
                overall_qual=qual,
                gr_liv_area=area,
                garage_cars=cars,
                total_bsmt_sf=bsmt,
                year_built=year,
                prediction=pred_value,
                predicted_on=datetime.utcnow()
            )
            add_entry(new_entry)
            
            flash(f"Success! Estimated Value: ${prediction_text}", "success")
        else:
            flash("Error: AI Model not loaded.", "danger")

    return render_template('predict.html', form=form, prediction=prediction_text)

@app.route('/history')
def history():
    if 'user' not in session: return redirect(url_for('login'))
    # Use the helper function to get data
    entries = get_entries()
    return render_template('history.html', history=entries)

@app.route('/delete_history/<int:id>')
def delete_history(id):
    if 'user' not in session: return redirect(url_for('login'))
    remove_entry(id)
    return redirect(url_for('history'))

# --- API ROUTE ---
@app.route('/api/predict', methods=['POST'])
def api_predict():
    if request.is_json:
        # ... (Keep your API logic here) ...
        return jsonify({'status': 'API Working'}), 200
    return jsonify({'error': 'Request must be JSON'}), 415