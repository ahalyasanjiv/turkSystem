import numpy as np
import pandas as pd
import hashlib
import datetime

class User:
    """
    User class. Has methods that inserts to and reads from the User table.
    """
    def __init__(self, first_name, last_name, email, phone, credit_card, type_of_user):
        df = pd.read_csv('database/User.csv')

        # hashed = self.hash_password(password)

        df.loc[len(df)] = pd.Series(data=[first_name, last_name, email, phone, credit_card, type_of_user],
                           index=['first_name', 'last_name', 'email', 'phone', 'credit_card', 'type_of_user'])
        df.to_csv('database/User.csv', index=False)

    def validate_user_id(self, user_id):
        """
        Validates the temporary user id, which should be unique from other user IDs.
        Returns True if the user ID is valid. Returns False otherwise.
        """
        df = pd.read_csv('database/User.csv')
        tmp = df.loc[df['temp_user_id'] == user_id]

        return tmp.empty

    def validate_password(self, password):
        """
        Validates the password, which should be longer than 8 characters.
        Returns True if the password is valid. Returns False otherwise.
        """
        return len(password) > 8

    def hash_password(self, password):
        """
        Returns the hash of the given password.
        """
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()

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

        hashed = self.hash_password(password)

        df.loc[len(df)] = pd.Series(data=[first_name, last_name, email,
                            phone, card_info, temp_user_id, hashed, type_of_user, 'pending'],
                           index=['first_name', 'last_name',
                           'email', 'phone', 'credit_card', 'user_id',
                           'password', 'type_of_user', 'status'])
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
        Validates the password, which should be longer than 8 characters.
        Returns True if the password is valid. Returns False otherwise.
        """
        return len(password) > 8

    def hash_password(self, password):
        """
        Returns the hash of the given password.
        """
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()

    @staticmethod
    def approve(user_id):
        """
        Approves the applicant and adds the user to the User table.
        After adding to the User table, the applicant's status is changed to approved.
        """
        df = pd.read_csv('database/Applicant.csv')
        # get the applicant's information from the table
        user = df.loc[df.user_id == user_id]

        # create a new row in the User table
        User(user['first_name'][0], user['last_name'][0], user['email'][0], user['phone'][0],
            user['credit_card'][0], user['type_of_user'][0])

        # update status
        df.loc[df.user_id == user_id, 'status'] = 'approved'
        df.to_csv('database/Applicant.csv', index=False)

    @staticmethod
    def reject(user_id):
        """
        Reject the applicant.
        """
        df = pd.read_csv('database/Applicant.csv')

        # update status
        df.loc[df.user_id == user_id, 'status'] = 'rejected'
        df.to_csv('database/Applicant.csv', index=False)

class Client:
    """
    Client class. Has methods that inserts to and reads from the Client table.
    """
    def __init__(self, user_id):
        df = pd.read_csv('database/Client.csv')

        df.loc[len(df)] = pd.Series(data=[user_id, 0, 0, 0, 0],
            index=['user_id', 'avg_rating', 'avg_given_rating', 'num_of_completed_projects', 'num_of_warnings'])
        df.to_csv('database/Client.csv', index=False)

class Developer:
    """
    Developer class. Has methods that inserts to and reads from the Developer table.
    """
    def __init__(self, user_id):
        df = pd.read_csv('database/Developer.csv')

        df.loc[len(df)] = pd.Series(data=[user_id, 0, 0, 0, 0],
            index=['user_id', 'avg_rating', 'avg_given_rating', 'num_of_completed_projects', 'num_of_warnings'])
        df.to_csv('database/Developer.csv', index=False)

class Demand:
    """
    Demand class. Has methods that inserts to, reads from, and modifies Demand table.
    """
    def __init__(self, client_id, date_posted, title, specifications, bidding_deadline):
        df = pd.read_csv('database/Demand.csv')

        now = datetime.datetime.now()
        date_posted = "{}-{}-{}".format(now.year, now.month, now.day)

        df.loc[len(df)] = pd.Series(data=[client_id, date_posted, title, specifications, bidding_deadline],
            index=['client_id', 'date_posted', 'title', 'specifications', 'bidding_deadline'])
        df.to_csv('database/Demand.csv', index=False)

class Bid:
    """
    Bid class. Has methods that inserts to Bid table.
    """
    def __init__(self, demand_id, developer_id, bid_amount):
        df = pd.read_csv('database/Bid.csv')
        df.loc[len(df)] = pd.Series(data=[demand_id, developer_id, bid_amount],
            index=['demand_id', 'developer_id', 'bid_amount'])
        df.to_csv('database/Bid.csv', index=False)

class BlacklistedUser:
    """
    BlacklistedUser class. Has methods that inserts to and reads from BlacklistedUser table.
    """
    def __init__(self, user_id):
        df = pd.read_csv('database/BlacklistedUser.csv')

        # get date for when the user can be taken off of blacklist
        # it is a year from the day when the user is put on the blacklist
        now = datetime.datetime.now()
        date = "{}-{}-{}".format(now.year + 1, now.month, now.day)

        df.loc[len(df)] = pd.Series(data=[user_id, date],
            index=['user_id', 'blacklisted_until'])
        df.to_csv('database/BlacklistedUser.csv', index=False)

class SuperUser:
    """
    SuperUser class.
    """
    def __init__(self, username, password):
        df = pd.read_csv('database/SuperUser.csv')

        hashed = self.hash_password(password)
        df.loc[len(df)] = pdf.Series(data=[username, hashed],
            index=['username', 'password'])

    def hash_password(self, password):
        """
        Returns the hash of the given password.
        """
        hash_object = hashlib.sha256(password.encode())
        return hash_object.hexdigest()
