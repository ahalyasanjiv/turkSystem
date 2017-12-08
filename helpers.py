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

def should_be_blacklisted(username):
	df = pd.read_csv('database/Warning.csv')
	get_warnings = df.loc[(df['warned_user'] == username) & ((df['status'] == 'active') | (df['status'] == 'active_and_denied'))]
	warnings = get_warnings.T.to_dict().values()
	num_of_warnings = len(warnings)
	if num_of_warnings >=2:
		return True
	return False
