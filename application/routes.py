import pandas as pd
import joblib
from application import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify
from application.form import PredictionForm, LoginForm, RegisterForm, UpdateAccountForm
from application.models import History, User
from datetime import datetime
from werkzeug.security import generate_password_hash ,check_password_hash
from flask_login import login_user, current_user, logout_user, login_required

# --- LOAD AI MODEL ---
try:
    model = joblib.load('housing_model.pkl')
except:
    model = None

# --- HELPER FUNCTIONS ---
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as error:
        db.session.rollback()
        flash(f"Database Error: {error}", "danger")
        return 0

def remove_entry(id):
    try:
        # [FIX] Use History instead of Entry
        entry = History.query.get(id)
        if entry:
            # [SECURITY] Ensure user can only delete their own history
            if entry.author != current_user:
                flash("You are not authorized to delete this.", "danger")
                return
            
            db.session.delete(entry)
            db.session.commit()
            flash("Record deleted successfully.", "success")
        else:
            flash("Entry not found.", "warning")
    except Exception as error:
        db.session.rollback()
        flash(f"Error: {error}", "danger")

# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Create new user
            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            
            flash(f"Account created for {form.username.data}! Please login.", "success")
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {e}", "danger")
            
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('predict'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            # [FIX] Use official Flask-Login function
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            
            # Handle "next" page redirect
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('predict'))
        else:
            flash("Invalid Username or Password", "danger")
            
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # [FIX] Use official Flask-Login logout
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        # Update Username
        current_user.username = form.username.data
        
        # Update Password (ONLY if they typed something)
        if form.password.data:
            # [FIX] Hash the new password before saving it to the database
            hashed_pw = generate_password_hash(form.password.data)
            current_user.password = hashed_pw
            
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
        
    elif request.method == 'GET':
        # Pre-fill the form with current data
        form.username.data = current_user.username

    return render_template('account.html', title='Account', form=form)


@app.route("/account/delete", methods=['POST'])
@login_required
def delete_account():
    user = current_user
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.', 'success')
        return redirect(url_for('register'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting account: {e}", "danger")
        return redirect(url_for('account'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required  # [FIX] Protect this route
def predict():
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
            pred_value = float(model.predict(input_df)[0])
            prediction_text = f"{pred_value:,.2f}"
            
            # 3. SAVE TO DB (Updated for new Relational DB)
            entry = History(
                # [FIX] Removed 'username=' because database handles it via author
                overall_qual=qual,
                gr_liv_area=area,
                garage_cars=cars,
                total_bsmt_sf=bsmt,
                year_built=year,
                prediction=pred_value,
                predicted_on=datetime.now(),
                author=current_user  # [FIX] Link to the logged-in user
            )
            add_entry(entry)
            
            flash(f"Success! Estimated Value: ${prediction_text}", "success")
        else:
            flash("Error: AI Model not loaded.", "danger")

    return render_template('predict.html', form=form, prediction=prediction_text)

@app.route('/history')
@login_required
def history():
    # 1. Base Query
    query = History.query.filter_by(author=current_user)

    # --- FILTERING LOGIC ---
    # We loop through all possible filters dynamically
    filters = {
        'quality': 'overall_qual',
        'area': 'gr_liv_area',
        'garage': 'garage_cars',
        'basement': 'total_bsmt_sf',
        'year': 'year_built'
    }

    for url_param, db_column in filters.items():
        value = request.args.get(url_param)
        if value and value.isdigit():
            # Apply exact match filter (e.g. WHERE overall_qual = 5)
            # getattr(History, db_column) gets the actual column object
            query = query.filter(getattr(History, db_column) == int(value))

    # --- SORTING LOGIC ---
    sort_col = request.args.get('sort', 'date') # Default to date
    sort_dir = request.args.get('order', 'desc') # Default to desc

    # Map URL sort keys to Database Columns
    sort_map = {
        'date': History.predicted_on,
        'quality': History.overall_qual,
        'area': History.gr_liv_area,
        'garage': History.garage_cars,
        'basement': History.total_bsmt_sf,
        'year': History.year_built,
        'price': History.prediction
    }

    # Apply Sort
    if sort_col in sort_map:
        column = sort_map[sort_col]
        if sort_dir == 'asc':
            query = query.order_by(column.asc())
        else:
            query = query.order_by(column.desc())

    # Execute
    entries = query.all()
    
    return render_template('history.html', history=entries)

@app.route('/delete_history/<int:id>')
@login_required
def delete_history(id):
    remove_entry(id)
    return redirect(url_for('history'))

# --- API ROUTE (Optional) ---
@app.route('/api/predict', methods=['POST'])
def api_predict():
    if request.is_json:
        # Placeholder for API logic
        return jsonify({'status': 'API Working'}), 200
    return jsonify({'error': 'Request must be JSON'}), 415














# [TEMPORARY FIX] Paste this at the bottom of routes.py
@app.route('/fix_db')
def fix_db():
    from application import db
    from application.models import User, History
    
    # 1. Create the tables
    db.create_all()
    
    # 2. Check if it worked
    try:
        user_count = User.query.count()
        return f"<h1>SUCCESS!</h1><p>Database tables created. Current users: {user_count}</p><p><a href='/register'>Go to Register</a></p>"
    except Exception as e:
        return f"<h1>Error</h1><p>{e}</p>"