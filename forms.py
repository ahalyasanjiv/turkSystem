from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class SignupForm(FlaskForm):
	"""Form for the page where the user signs up"""
	first_name = StringField(label='First Name', id='first_name', validators=[DataRequired('Please enter your first name.')])
	last_name = StringField(label='Last Name', id='last_name', validators=[DataRequired('Please enter your last name.')])
	email = StringField(label='Email Address', id='email', validators=[DataRequired('Please enter an email address.'), Email(message='Please enter a valid email address.')])
	username = StringField(label='Username', id='username', validators=[DataRequired('Please enter a username.')])
	password = StringField(label='Password', id='password', validators=[DataRequired('Please enter a password.')])

class SigninForm(FlaskForm):
	"""Form for the page where the user signs in"""
	username = StringField(label='Username', id='username', validators=[DataRequired('Please enter your username.')])
	password = StringField(label='Password', id='password', validators=[DataRequired(''), EqualTo('confirm_password', message='The passwords must match.')])






