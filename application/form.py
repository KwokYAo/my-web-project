from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError,EqualTo
from application.models import User

class PredictionForm(FlaskForm):
    # 1. Overall Quality (1-10)
    overall_qual = IntegerField('Overall Material Quality', validators=[
        InputRequired(message="Please enter a valid number."),
        NumberRange(min=1, max=10, message="Quality must be between 1 and 10")
    ])

    # 2. Living Area (Sq Ft)
    gr_liv_area = IntegerField('Living Area (sq ft)', validators=[
        InputRequired(message="Please enter a valid number."),
        NumberRange(min=0, message="Area cannot be negative")
    ])

      # FIX: Use InputRequired() instead of DataRequired() to allow '0'
    garage_cars = SelectField('Garage Capacity', coerce=int, choices=[
        (0, 'No Garage'),
        (1, '1 Car'),
        (2, '2 Cars'),
        (3, '3 Cars'),
        (4, '4+ Cars')
    ], validators=[InputRequired(message="Please select a garage size")])

    # 4. Basement Area (Sq Ft)
    total_bsmt_sf = IntegerField('Total Basement Area (sq ft)', validators=[
        InputRequired(message="Please enter a valid number."),
        NumberRange(min=0, message="Basement area cannot be negative")
    ])

    # 5. Year Built
    year_built = IntegerField('Year Built', validators=[
        InputRequired(message="Please enter a valid number."),
        NumberRange(min=1900, max=2030, message="Year must be between 1800 and 2030")
    ])

    submit = SubmitField('Calculate Price')

    # CUSTOM VALIDATOR (The "Extra Mile" for robustness)
    # This runs automatically when you call form.validate()
    def validate_year_built(self, year_built):
        if year_built.data is None:
             raise ValidationError("Invalid input: Please enter a numeric year.")
        

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(), 
        Length(min=4, max=25, message="Username must be 4-25 chars")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(), 
        Length(min=4, message="Password must be at least 4 chars")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        InputRequired(), 
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register Account')

    # Custom Validator: Check if username already exists
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose another.')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username is required"),
        Length(min=4, max=25, message="Username must be between 4 and 25 characters")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password is required"),
        Length(min=4, message="Password must be at least 4 characters")
    ])
    submit = SubmitField('Login')