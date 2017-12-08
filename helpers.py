"""
Module of helper functions
"""
import hashlib
import pandas as pd
from csv import reader

def hash_password(password):
    """
    Returns the hash of the given password.
    """
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()

def get_protests():
	df = pd.read_csv('database/Warning.csv')
	get_protests = df.loc[df['status'] == 'pending']
	protests = get_protests['warning_id'].values.tolist()
	return protests

def get_pending_applicants():
	df = pd.read_csv('database/Applicant.csv')
	get_apps = df.loc[df['status'] == 'pending']
	pending_applicants = get_apps['user_id'].values.tolist()
	return pending_applicants

def get_user_warnings(username):
	df = pd.read_csv('database/Warning.csv')
	get_warnings = df.loc[df['warned_user'] == username]
	warnings = get_warnings.T.to_dict().values()
	return warnings

def get_pending_transactions():
	df = pd.read_csv('database/Transaction.csv')
	get_pending_transactions = df.loc[df['status'] == 'pending']
	pending_transactions = get_pending_transactions.T.to_dict().values()
	return pending_transactions

def should_be_blacklisted(username):
	df = pd.read_csv('database/Warning.csv')
	get_warnings = df.loc[df['warned_user'] == username]
	warnings = get_warnings.T.to_dict().values()
	num_of_warnings = 0
	for warning in warnings:
		if warning['status'] == 'active' or warning['status'] == 'active_and_denied':
			num_of_warnings+=1
		if num_of_warnings >=2:
			return True
	return False
	# num_of_warnings = len(warnings0 + warnings1)
	# if num_of_warnings >=2:
	# 	return True
	# return False

def does_user_have_enough_money(username,money):
	df = pd.read_csv('database/User.csv')
	user = df.loc[df.username == username]
	type_of_user = user['type_of_user'].item()
	balance = 0
	if type_of_user == 'client':
		df = pd.read_csv('database/Client.csv')
		user = df.loc[df.username == username]
		balance = user['balance'].item()
	elif type_of_user == 'developer':
		df = pd.read_csv('database/Developer.csv')
		user = df.loc[df.username == username]
		balance = user['balance'].item()
	return balance >= money

