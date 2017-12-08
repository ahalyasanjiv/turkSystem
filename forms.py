from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, SubmitField, SelectField, TextAreaField, DateField, ValidationError, DecimalField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, InputRequired
from models import Applicant, Bid

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

def validate_bid_amount(form, field, demand_id):
	"""
	Custom validator for BidForm.
	Validates if bid_amount is less than the lowest bid, if there is any.
	Also validates that bid_amount is a positive number.
	"""
	bids = Bid.get_bids_for_demand(demand_id)

	if len(bids) > 0:
		lowest_bid_amount = Bid.get_info(bids[0]).bid_amount

		if float(field.data) >= float(lowest_bid_amount):
			print(field.data)
			raise ValidationError('Bid must be lower than the currently lowest bid.')

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
	Form for the page where the superuser can approve/reject an applicant
	"""
	decision = SelectField(label='Decision', id='decision', validators=[DataRequired('Please select a decision.')], choices = [('approve','Approve'),('reject','Reject')],)
	reason = TextAreaField(label='Reason for Decision', validators=[DataRequired('Please provide a reason.')])
	submit = SubmitField('Submit')

class ProtestApprovalForm(FlaskForm):
	"""
	Form for the page where the superuser can remove or keep a user's warning if the user has filed a protest against the warning 
	"""
	decision = SelectField(label='Decision', id='decision', validators=[DataRequired('Please select a decision.')], choices = [('remove','Remove Warning'),('keep','Keep Warning')],)
	submit = SubmitField('Submit')



class ProtestForm(FlaskForm):
	""" 
	Form for when user wants to protest a warning. 
	"""
	reason = TextAreaField(label='Reason for Protesting Warning', id='reason', validators=[DataRequired('Please enter a reason for protesting this warning.')])
	submit = SubmitField('Submit Protest')

class DemandForm(FlaskForm):
	"""
	Form for clients to create and post a demand.
	"""
	title = StringField(label='System Title', id='title',
						validators=[DataRequired('Please enter a title for your demand.')])
	tags = StringField(label='Tags')
	specifications = TextAreaField(label='System description',
					 id='specifications',
					 validators=[DataRequired('Please enter specifications for the demand.')])
	bidding_deadline = DateField(label='Deadline for Bidding', id='bidding_deadline',
					 validators=[DataRequired('Please provide a deadline for bidding.')])
	submission_deadline = DateField(label='Deadline for Submitting the System', id='submission_deadline',
					 validators=[DataRequired('Please provide a deadline for submitting the final system.')])
	submit = SubmitField('Post Demand')

class BidForm(FlaskForm):
	"""
	Form for developers to make bids for a demand.
	"""
	bid_amount = DecimalField(label='Bid Amount', id='bid_amount', validators=[DataRequired('Please enter an amount to bid.')])
	# , validate_bid_amount])
	submit = SubmitField('Make a Bid')

class JustifyDeveloperChoiceForm(FlaskForm):
	"""
	Form for clients to justify their reason for choosing a developer who did
	not submit the lowest bid for their system demand.
	"""
	reason = TextAreaField(label='Reason for not choosing the developer with the lowest bid.',
						   validators=[DataRequired('Please provide a reason for not choosing the developer with the lowest bid.')])
	submit = SubmitField('Submit Reason')

class BecomeUserForm(FlaskForm):
	"""
	Form for when applicant wants to become user
	"""
	use_prev_credentials = SelectField(label='Do you want to keep your current login credentials?', id='use_prev_credentials', validators=[DataRequired('Please choose a role.')], choices = [('yes','Yes'),('no','No')],)
	username = StringField(label='User ID', id='user_id', validators=[DataRequired('Please enter a user ID.'), validate_user_id])
	password = PasswordField(label='Password', id='password', validators=[DataRequired('Please enter a password.'), Length(min=8, message='Your password must have at least 8 characters.')])
	confirm_password = PasswordField(label='Confirm Password', id='confirm_password', validators=[DataRequired('Please confirm your password.')])
	submit = SubmitField('Submit')

class SubmitSystemForm(FlaskForm):
	"""
	Form for a developer to submit a system for a client's demand.
	"""
	system = FileField('System file', validators=[DataRequired('Please submit a file containing the system.')])
	submit = SubmitField('Submit')

class RatingForm(FlaskForm):
	"""
	Form for rating after a project is finished.
	"""
	rating = RadioField(label='Rating', 
		choices=[
		(1,'<i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i>'),
		(2,'<i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i>'),
		(3,'<i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i>'),
		(4, '<i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star-o" aria-hidden="true"></i>'),
		(5,'<i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i><i class="fa fa-star" aria-hidden="true"></i>')], 
		coerce=int)
	submit = SubmitField('Submit')

class RatingMessageForm(FlaskForm):
	"""
	Form for sending message after a low rating.
	"""
	message = TextAreaField(label='Send Feedback', id="message", validators=[DataRequired('Please give a rating.')] )
	submit = SubmitField('Submit')

class TransactionApprovalForm(FlaskForm):
	"""
	Form for the page where the superuser can approve/reject a transaction
	"""
	decision = SelectField(label='Please select your decision', id='decision', validators=[DataRequired('Please choose an option.')], choices = [('approve','Approve'),('deny','Deny')],)
	submit = SubmitField('Submit')
