import numpy as np
import pandas as pd
import hashlib
import datetime
from werkzeug import generate_password_hash, check_password_hash

class User:
    """
    User class. Has methods that inserts to and reads from the User table.
    """
    def __init__(self, first_name, last_name, email, phone, credit_card, type_of_user):
        df = pd.read_csv('database/User.csv')

        df.loc[len(df)] = pd.Series(data=[first_name, last_name, email, phone, credit_card, type_of_user],
                           index=['first_name', 'last_name', 'email', 'phone', 'credit_card', 'type_of_user'])
        df.to_csv('database/User.csv', index=False)

    def set_credentials(self, username, password, email):
        """
        After a user is approved, the user can set his/her official username and password.
        This method stores this information in the User table.
        """
        df = pd.read_csv('database/User.csv')
        df.loc[df.email == email, 'username'] = username
        df.loc[df.email == email, 'password'] = hash_password(password)
        df.to_csv('database/User.csv', index=False)

    def has_user_id(self, username):
        """
        Returns True if the username exists in the User table.
        Returns False otherwise.
        """
        df = pd.read_csv('database/User.csv')
        tmp = df.loc[df['username'] == username]

        return not tmp.empty

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
    def check_password(username, password):
        """
        Checks if the password of a username match. 
        Returns true if password given matches the password for username 
        given and false if the password does not match.
        """
        df = pd.read_csv('database/User.csv')
        user = df.loc[df['username'] == username]
        if not user.empty:
            pwhash = user['password'][0]
            return check_password_hash(pwhash,generate_password_hash(password))
        return False
        

    @staticmethod
    def get_user_info(username):
        """
        Returns a dictionary of the user's information.
        """
        df = pd.read_csv('database/User.csv')
        user = df.loc[df['username'] == username]

        if not user.empty:
            return {'username': username,
                    'first_name': user['first_name'].item(),
                    'last_name': user['last_name'].item(),
                    'email': user['email'].item(),
                    'phone': user['phone'].item(),
                    'type_of_user': user['type_of_user'].item(),
                    'about': user['about'].item(),
                    'link_to_user': '/user/' + username}

    @staticmethod
    def set_about(username, about):
        """
        Modifies the user's about/info.
        """
        df = pd.read_csv('database/User.csv')
        user = df.loc[df['username'] == username]

        if not user.empty:
            df.loc[df.username == username, 'about'] = about
            df.to_csv('database/User.csv')

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

    def has_user_id(self, user_id):
        """
        Validates the temporary user id, which should be unique from other user IDs.
        Returns True if the user ID already exists in the Applicant table.
        Returns False if the user ID does not already exist.
        """
        df = pd.read_csv('database/Applicant.csv')
        tmp = df.loc[df['temp_user_id'] == user_id]

        return not tmp.empty

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
        # get the applicant's information from the table
        df = pd.read_csv('database/Applicant.csv')
        user = df.loc[df.user_id == user_id]

        if not user.empty:
            if user['status'].item() == 'pending':
                # create a new row in the User table
                User(user['first_name'].item(), user['last_name'].item(), user['email'].item(), user['phone'].item(),
                    user['credit_card'].item(), user['type_of_user'].item())

                # update status
                df.loc[df.user_id == user_id, 'status'] = 'approved'
                df.to_csv('database/Applicant.csv', index=False)

                # add the user to the corresponding table
                if user['type_of_user'].item() == 'client':
                    Client(user_id)
                elif user['type_of_user'].item() == 'developer':
                    Developer(user_id)

    @staticmethod
    def reject(user_id):
        """
        Reject the applicant. The applicant's status is changed to rejected.
        """
        df = pd.read_csv('database/Applicant.csv')
        user = df.loc[df.user_id == user_id]

        if user['status'].item() == 'pending':
            # update status
            df.loc[df.user_id == user_id, 'status'] = 'rejected'
            df.to_csv('database/Applicant.csv', index=False)

class Demand:
    """
    Demand class. Has methods that inserts to, reads from, and modifies Demand table.
    """
    def __init__(self, client_username, title, tags, specifications, bidding_deadline, submission_deadline):
        df = pd.read_csv('database/Demand.csv')

        now = datetime.datetime.now()
        format = '%m-%d-%Y %I:%M %p'
        date_posted = now.strftime(format)
        
        df.loc[len(df)] = pd.Series(data=[client_username, date_posted, title, tags, specifications, bidding_deadline, submission_deadline],
            index=['client_username', 'date_posted', 'title', 'tags', 'specifications', 'bidding_deadline', 'submission_deadline'])

        df.to_csv('database/Demand.csv', index=False)

    @staticmethod
    def get_info(title): # need to add id column so we can get demand by id instead
        """
        Returns a dictionary of information for the specified demand.
        """
        df = pd.read_csv('database/Demand.csv')
        demand = df.loc[df.title == title]

        now = datetime.datetime.now()
        deadline_passed = datetime.datetime.strptime(demand['bidding_deadline'].item(), '%m-%d-%Y %I:%M %p') < now

        if not demand.empty:
            return {'client_username': demand['client_username'].item(),
                    'date_posted': demand['date_posted'].item(),
                    'title': demand['title'].item(),
                    'tags': demand['tags'].item(),
                    'specifications': demand['specifications'].item(),
                    'bidding_deadline': demand['bidding_deadline'].item(),
                    'submission_deadline': demand['submission_deadline'].item(),
                    'bidding_deadline_passed': deadline_passed,
                    'link_to_client': '/user/' + demand['client_username'].item(),
                    'link_to_demand': '/bid/' + str(demand.index[0])}

    @staticmethod
    def get_all_demands():
        """
        Returns a list of all demands.
        The demands are ordered from most recent to least recent.
        """
        df = pd.read_csv('database/Demand.csv')
        demands = []

        for index, row in df.iterrows():
            demands.append(row['title'])
        return demands[::-1]

    @staticmethod
    def get_all_active_demands():
        """
        Returns a list of active demands. The bidding deadline for Active demands have not passed yet.
        """
        df = pd.read_csv('database/Demand.csv')
        now = datetime.datetime.now().date()
        active_demands = []

        for index, row in df.iterrows():
            tmp_date = datetime.datetime.strptime(row['bidding_deadline'], '%m-%d-%Y %I:%M %p').date()
            if tmp_date > now:
                active_demands.append(row['title'])

        return active_demands

class Bid:
    """
    Bid class. Has methods that inserts to Bid table.
    """
    def __init__(self, demand_id, developer_id, bid_amount):
        df = pd.read_csv('database/Bid.csv')
        df.loc[len(df)] = pd.Series(data=[demand_id, developer_id, bid_amount],
            index=['demand_id', 'developer_id', 'bid_amount'])
        df.to_csv('database/Bid.csv', index=False)

    @staticmethod
    def get_info(bid_id):
        """
        Returns a dictionary of information for the bid specified by the given index.
        Argument bid_id is the index of the row for the bid in the Bid table.
        """
        df = pd.read_csv('database/Bid.csv')
        bid = df.loc[bid_id]

        return {'demand_id': bid['demand_id'],
                'developer_username': bid['developer_username'],
                'bid_amount': bid['bid_amount']}

    @staticmethod
    def get_bids_for_demand(demand_id):
        """
        Returns a list of bid_ids or indexes where the bids are located in the Bid table.
        """
        df = pd.read_csv('database/Bid.csv')
        bids = df.loc[df['demand_id'] == int(demand_id)]

        return bids.index.tolist()

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
