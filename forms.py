from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField, TextAreaField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignupForm(FlaskForm):
	""" Form for the page where the user signs up. """
	first_name = StringField(label='First Name', id='first_name', validators=[DataRequired('Please enter your first name.')])
	last_name = StringField(label='Last Name', id='last_name', validators=[DataRequired('Please enter your last name.')])
	email = StringField(label='Email Address', id='email', validators=[DataRequired('Please enter an email address.'), Email(message='Please enter a valid email address.')])
	username = StringField(label='Username', id='username', validators=[DataRequired('Please enter a username.')])
	password = StringField(label='Password', id='password', validators=[DataRequired('Please enter a password.'), Length(min=8, message='Your password must have at least 8 characters.')])
	confirm_password = PasswordField('Input Password Again')
	role = RadioField(label='Role', id='role', validators=[DataRequired('Please choose a role.')], choices = [('client','Client'),('developer','Developer')],)
	submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
	""" Form for the page where the user signs in. """
	username = StringField(label='Username', id='username', validators=[DataRequired('Please enter your username.')])
	password = StringField(label='Password', id='password', validators=[DataRequired('Please enter your password.')])
	submit = SubmitField('Sign in')

class ProtestForm(FlaskForm):
	""" Form for when user wants to protest a warning. """
	warning = SelectField(label='Warning to Protest', choices = [('warning1','Warning#1'),('warning2','Warning#2')])
	reason = TextAreaField(label='Reason for Protest', id='reason', validators=[DataRequired('Please enter a reason for protesting this complaint.')])
	submit = SubmitField('Submit Protest')

