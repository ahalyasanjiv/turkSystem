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