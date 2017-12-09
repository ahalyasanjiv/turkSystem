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

