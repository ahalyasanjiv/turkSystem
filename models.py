import numpy as np
import pandas as pd
import hashlib

class TurkSystem:
    """
    A python singleton class that keeps track of the Turk System's statistics.
    """

    def __init__(self):
        self.num_of_users = 0
        self.num_of_clients = 0
        self.num_of_developers = 0
        self.num_of_demands = 0
        self.next_available_user_id = 0
        self.next_available_demand_id = 0

    def increment_user_id(self):
        self.next_available_user_id += 1

    def increment_demand_id(self):
        self.next_available_demand_id += 1

turk = TurkSystem()

class Applicant:
    """
    Applicant class. Has methods that inserts to and reads from the Applicant table.
    """
    def __init__(self, type_of_user, first_name, last_name, email, phone,
                 card_info, temp_user_id, password):
        """
        Create a new applicant and store the information in the database.
        """
        df = pd.read_csv('database/Applicant.csv')

        app_id = turk.next_available_user_id
        turk.increment_user_id()

        hashed = self.hash_password(password)

        df.loc[len(df)] = pd.Series(data=[app_id, first_name, last_name, email,
                            phone, card_info, temp_user_id, hashed, type_of_user],
                           index=['id', 'first_name', 'last_name',
                           'email', 'phone', 'credit_card', 'temp_user_id',
                           'temp_password', 'type_of_user'])
        df.to_csv('database/Applicant.csv', index=False)

    def validate_email(self, email):
        """
        Validates the email, which should be unique from other emails.
        The email should also be in the correc format.
        Returns True if the email is valid. Returns False otherwise.
        """
        df = pd.read_csv('database/Applicant.csv')
        tmp = df.loc[df['email'] == email]

        # also validate the format of the email using regex

        return tmp.empty

    def validate_user_id(self, user_id):
        """
        Validates the temporary user id, which should be unique from other user IDs.
        Returns True if the user ID is valid. Returns False otherwise.
        """
        df = pd.read_csv('database/Applicant.csv')
        tmp = df.loc[df['temp_user_id'] == user_id]

        return tmp.empty

    def validate_password(self, password):
        """
        Validates the password, which should be at least 6 characters long.
        Returns True if the password is valid. Returns False otherwise.
        """
        return len(password) >= 6

    def hash_password(self, password):
        """
        Returns the hash of the given password.
        """
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()

class User:
    """
    User class. Has methods that inserts to and reads from the User table.
    """
    def __init__(self, id, username, password, first_name, last_name, email, phone, type_of_user):
        df = pd.read_csv('database/User.csv')

        hashed = self.password_hash(self, password)

        df.loc[len(df)] = pd.Series(data=[id, username, password, email, first_name, last_name, email, type_of_user],
                           index=['id', 'username', hashed, first_name,last_name,type_of_user])
        df.to_csv('database/Applicant.csv', index=False)



