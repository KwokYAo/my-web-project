from application import app
from flask import render_template, request, redirect, url_for, session, flash
from datetime import datetime

# --- MOCK DATA (Temporary, until you add Database) ---
# This allows the History page to look real without a DB connection.
mock_history = [
    {'id': 1, 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"), 'overall_qual': 7, 'gr_liv_area': 1500, 'garage_cars': 2, 'year_built': 2005, 'prediction': 215000.00},
    {'id': 2, 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"), 'overall_qual': 5, 'gr_liv_area': 900, 'garage_cars': 1, 'year_built': 1960, 'prediction': 120500.00}
]

# --- ROUTES ---

# Handles http://127.0.0.1:5000/hello
@app.route('/hello')
def hello_world():
    return "<h1>Hello Ames Housing AI</h1>"

# Handles Home Page (Root, Index, Home)
@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    return render_template("index.html", title="Welcome to Ames AI")

# Handles Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # MOCK LOGIN LOGIC (Accepts password 'password')
        if password == 'password':
            session['user'] = username
            flash(f"Successfully logged in as {username}!", "success")
            return redirect(url_for('predict'))
        else:
            flash("Invalid Credentials. Try password: 'password'", "danger")
            return render_template('login.html', error="Invalid Credentials")
            
    return render_template('login.html')

# Handles Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# Handles Prediction Dashboard
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    # if 'user' not in session: 
    #     flash("Please login to access the dashboard.", "warning")
    #     return redirect(url_for('login'))
    
    prediction_text = None
    
    if request.method == 'POST':
        try:
            # 1. Get Data from HTML Form
            qual = int(request.form['OverallQual'])
            area = int(request.form['GrLivArea'])
            cars = int(request.form['GarageCars'])
            bsmt = int(request.form['TotalBsmtSF'])
            year = int(request.form['YearBuilt'])

            # 2. Validation (TDD Logic)
            if not (1 <= qual <= 10):
                return render_template('predict.html', error="Quality must be 1-10")
            
            # 3. MOCK PREDICTION (No AI Model yet)
            # Simple formula to simulate a result so you can see the UI
            pred_value = (qual * 10000) + (area * 100) + (cars * 5000) + (year * 10)
            prediction_text = f"{pred_value:,.2f}"
            
            # 4. Mock Saving to History (Append to list instead of DB)
            new_entry = {
                'id': len(mock_history) + 1,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'overall_qual': qual, 'gr_liv_area': area, 
                'garage_cars': cars, 'year_built': year,
                'prediction': pred_value
            }
            mock_history.insert(0, new_entry) # Add to top of list
            
            flash("Prediction calculated successfully!", "success")

        except ValueError:
            return render_template('predict.html', error="Invalid input. Please enter numbers.")

    return render_template('predict.html', prediction=prediction_text)

# Handles History Page
@app.route('/history')
def history():
    if 'user' not in session: return redirect(url_for('login'))
    
    # Pass the mock_history list to the template
    return render_template('history.html', history=mock_history)

# Handles Deleting History
@app.route('/delete_history/<int:id>')
def delete_history(id):
    if 'user' not in session: return redirect(url_for('login'))
    
    # Mock Deletion
    global mock_history
    mock_history = [row for row in mock_history if row['id'] != id]
    
    flash("Record deleted.", "success")
    return redirect(url_for('history'))