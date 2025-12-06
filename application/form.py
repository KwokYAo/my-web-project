from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from application.models import User

# 1. Prediction Form
class PredictionForm(FlaskForm):
    overall_qual = IntegerField("Overall Material Quality", validators=[DataRequired()])
    gr_liv_area = IntegerField("Living Area (sq ft)", validators=[DataRequired()])
    garage_cars = SelectField("Garage Capacity", coerce=int, choices=[
        (0, "No Garage"), (1, "1 Car"), (2, "2 Cars"), (3, "3 Cars"), (4, "4+ Cars")
    ])
    total_bsmt_sf = IntegerField("Total Basement Area (sq ft)", validators=[DataRequired()])
    year_built = IntegerField("Year Built", validators=[DataRequired()])
    submit = SubmitField("Calculate Price")

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