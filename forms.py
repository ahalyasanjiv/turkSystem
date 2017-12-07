from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField, TextAreaField, DateField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models import Applicant

def validate_user_id(form,field):
	"""
	Custom validator for username
	:returns: True if username is unique and is not equal to ' ', False if username is not unique or is equal to ' '.
	"""
	if not Applicant.is_unique_user_id(field.data) or field.data == ' ':
		raise ValidationError('User ID is taken. Please enter another User ID.')

def validate_email(form,field):
	"""
	Custom validator for username
	:returns: True if username is unique and False if username is not unique.
	"""
	if not Applicant.is_unique_email(field.data):
		raise ValidationError('There already exists an account with this email.')



class SignupForm(FlaskForm):
	""" 
	Form for the page where the user signs up. 
	"""
	first_name = StringField(label='First Name', id='first_name', validators=[DataRequired('Please enter your first name.')])
	last_name = StringField(label='Last Name', id='last_name', validators=[DataRequired('Please enter your last name.')])
	email = StringField(label='Email Address', id='email', validators=[DataRequired('Please enter an email address.'), Email(message='Please enter a valid email address.'), validate_email])
	phone = StringField(label='Phone Number', id='phone', validators=[DataRequired('Please enter a phone number.')])
	user_id = StringField(label='User ID', id='user_id', validators=[DataRequired('Please enter a user ID.'), validate_user_id])
	password = PasswordField(label='Password', id='password', validators=[DataRequired('Please enter a password.'), Length(min=8, message='Your password must have at least 8 characters.')])
	confirm_password = PasswordField(label='Confirm Password', id ='confirm_password', validators=[DataRequired('Please confirm your password.')])
	credit_card = StringField(label='Credit Card Number', id='credit_card', validators=[DataRequired('Please enter the credit card number.')])
	credit_card_name = StringField(label='Name of Credit Card Holder', id='credit_card_number', validators=[DataRequired('Please enter the name of the credit card holder.')])
	exp_date = DateField(label='Expiration Date', id='credit_card_exp_date', validators=[DataRequired('Please enter the credit card expiration date.')], format='%m/%Y')
	security_code = StringField(label='Security Code', id='security_code', validators=[DataRequired('Please enter the security code.')])
	billing_address = StringField(label='Billing Address', id='billing_address', validators=[DataRequired('Please enter the billing address.')])
	role = SelectField(label='Role', id='role', validators=[DataRequired('Please choose a role.')], choices = [('client','Client'),('developer','Developer')],)
	submit = SubmitField('Sign up')

class LoginForm(FlaskForm):
	""" 
	Form for the page where the user signs in. 
	"""
	username = StringField(label='Username', id='username', validators=[DataRequired('Please enter your username.')])
	password = PasswordField(label='Password', id='password', validators=[DataRequired('Please enter your password.')])
	submit = SubmitField('Sign in')

class ApplicantApprovalForm(FlaskForm):
	"""
	Form for the page where the superuser 
	"""
	accept = SubmitField(label='Accept')
	reject = SubmitField(label='Reject')

class ProtestForm(FlaskForm):
	""" 
	Form for when user wants to protest a warning. 
	"""
	warning = SelectField(label='Warning to Protest', choices = [('warning1','Warning#1'),('warning2','Warning#2')])
	reason = TextAreaField(label='Reason for Protest', id='reason', validators=[DataRequired('Please enter a reason for protesting this complaint.')])
	submit = SubmitField('Submit Protest')

class BecomeUserForm(FlaskForm):
	"""
	Form for when applicant wants to become user
	"""
	username = username = StringField(label='Username', id='username', validators=[DataRequired('Please enter your username.')])
	password = PasswordField(label='Password', id='password', validators=[DataRequired('Please enter your password.')])
	confirm_password = PasswordField(label='Confirm Password', id ='confirm_password', validators=[DataRequired('Please confirm your password.')])
