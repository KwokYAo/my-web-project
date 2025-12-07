from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange ,InputRequired
from flask_login import current_user
from application.models import User

# 1. Prediction Form
class PredictionForm(FlaskForm):
    # --- 1. Material Quality (Was missing, caused Server Error) ---
    overall_qual = IntegerField('Overall Material Quality', validators=[
        InputRequired(),
        NumberRange(min=1, max=10, message="Quality must be between 1 and 10")
    ])

    # --- 2. Living Area (Cannot be 0) ---
    gr_liv_area = IntegerField('Living Area (sq ft)', validators=[
        InputRequired(), 
        NumberRange(min=1, message="Area must be at least 1 sq ft")
    ])

    # --- 3. Garage Capacity (Was missing) ---
    # We use InputRequired() so "0" (No Garage) is accepted as a valid answer.
    garage_cars = SelectField('Garage Capacity', coerce=int, choices=[
        (0, 'No Garage'),
        (1, '1 Car'),
        (2, '2 Cars'),
        (3, '3+ Cars')
    ], validators=[InputRequired()])

    # --- 4. Basement (Can be 0) ---
    # We use InputRequired() here too. DataRequired() would block "0".
    total_bsmt_sf = IntegerField('Total Basement Area (sq ft)', validators=[
        InputRequired(), 
        NumberRange(min=0, message="Area cannot be negative")
    ])

    # --- 5. Year Built ---
    year_built = IntegerField('Year Built', validators=[
        InputRequired(), 
        NumberRange(min=1900, max=2026, message="Year must be between 1900 to 2026")
    ])

    submit = SubmitField('Calculate Price')

# 2. Registration Form
class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("That username is already taken. Please choose a different one.")

# 3. Login Form
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")

# 4. Account Update Form
class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField("New Password (Leave blank to keep current)")
    confirm_password = PasswordField("Confirm New Password", validators=[EqualTo('password')])
    submit = SubmitField("Update Profile")

    def validate_username(self, username):
        # Only check if they actually changed it
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("That username is already taken. Please choose a different one.")