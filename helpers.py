"""
Module of helper functions
"""
import hashlib

def hash_password(password):
    """
    Returns the hash of the given password.
    """
    hash_object = hashlib.sha256(password.encode())
    return hash_object.hexdigest()