import numpy as np
import pandas as pd
import hashlib
import datetime
from werkzeug import generate_password_hash, check_password_hash
import re
from helpers import hash_password

class User:
    """
    User class. Has methods that inserts to and reads from the User table.
    """
    def __init__(self, first_name, last_name, email, phone, credit_card, type_of_user):
        df = pd.read_csv('database/User.csv')

        df.loc[len(df)] = pd.Series(data=[' ', ' ', first_name, last_name, email, phone, credit_card, type_of_user],
                           index=['username', 'password', 'first_name', 'last_name', 'email', 'phone', 'credit_card', 'type_of_user'])
        df.to_csv('database/User.csv', index=False)

    def has_user_id(self, username):
        """
        Returns True if the username exists in the User table.
        Returns False otherwise.
        """
        df = pd.read_csv('database/User.csv')
        tmp = df.loc[df['username'] == username]

        return not tmp.empty

    @staticmethod
    def set_credentials(username, password, email):
        """
        After a user is approved, the user can set his/her official username and password.
        This method stores this information in the User table.
        """
        # Change the login credentials in Applicant database
        df = pd.read_csv('database/Applicant.csv')
        df.loc[df.email == email, 'username'] = username
        df.loc[df.email == email, 'password'] = hash_password(password)
        df.to_csv('database/Applicant.csv', index=False)
        # Change the login credentials in User database
        df = pd.read_csv('database/User.csv')
        df.loc[df.email == email, 'username'] = username
        df.loc[df.email == email, 'password'] = hash_password(password)
        df.to_csv('database/User.csv', index=False)

    
    @staticmethod
    def use_old_credentials(username, email):
        """
        After a user is approved, the user can keep their old username and password.
        This method stores this information in the User table.
        """
        df = pd.read_csv('database/Applicant.csv')
        password = df.loc[df.user_id == username, 'password']
        df = pd.read_csv('database/User.csv')
        df.loc[df.email == email, 'username'] = username
        df.loc[df.email == email, 'password'] = password
        df.to_csv('database/User.csv', index=False)

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
            pwhash = user['password'].item()
            return pwhash == hash_password(password)  

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

    @staticmethod
    def get_number_of_users():
        """
        Returns the number of users stored in the database. Excludes NaNs.
        """
        df = pd.read_csv('database/User.csv')
        return df['username'].count() # does not count NaNs

class Client:
    """
    Client class. Has methods that inserts to and reads from the Client table.
    """
    def __init__(self, username):
        df = pd.read_csv('database/Client.csv')

        df.loc[len(df)] = pd.Series(data=[username, 0, 0, 0, 0, 100],
            index=['username', 'avg_rating', 'avg_given_rating', 'num_of_completed_projects', 'num_of_warnings', 'balance'])
        df.to_csv('database/Client.csv', index=False)

    @staticmethod
    def get_info(username):
        """
        Returns a dictionary of information for the given developer.
        """
        df = pd.read_csv('database/Client.csv')
        client = df.loc[df.username == username]

        return {'username': username,
                'avg_rating': client['avg_rating'].item(),
                'avg_given_rating': client['avg_given_rating'].item(),
                'num_of_completed_projects': client['num_of_completed_projects'].item(),
                'num_of_warnings': client['num_of_warnings'].item()}

    @staticmethod
    def get_projects_posted(username):
        """
        Returns a list of all demands that the client posted.
        """
        df = pd.read_csv('database/Demand.csv')
        projects = df.loc[df.client_username == username]

        return projects.index.tolist()

    @staticmethod
    def get_number_of_clients():
        """
        Returns the number of clients in the client database. Excludes NaNs.
        """
        df = pd.read_csv('database/Client.csv')
        return df['username'].count() # does not count NaNs

    @staticmethod
    def get_most_active_clients():
        """
        Returns the top 3 clients with the most projects completed.
        """
        df = pd.read_csv('database/Client.csv')
        sorted_df = df.sort_values(by='num_of_completed_projects', ascending=False)
        sorted_df = sorted_df.iloc[:3]

        usernames = []
        for index, row in sorted_df.iterrows():
            usernames.append(User.get_user_info(row['username']))

        return usernames

    @staticmethod
    def get_clients_with_most_projects():
        """
        Returns the top 3 clients with the most projects, completed or not.
        This is used on the index page.
        """
        df = pd.read_csv('database/Demand.csv')
        projects = df.groupby(['client_username']).size()
        projects = projects.sort_values(ascending=False)

        usernames = []
        for index, value in projects.iteritems():
            if len(usernames) == 3:
                break;
            usernames.append(index)

        return usernames

    @staticmethod
    def get_similar_clients(username):
        """
        Returns three clients with similar interests as the specified user, based
        on tags of the user's most recent completed projects.
        """
        projects = []
        user_type = User.get_user_info(username)['type_of_user']
        if user_type == 'client':
            projects = Client.get_projects_posted(username)
        else: #is developer
            projects = Developer.get_past_projects(username)
        
        tags = ""
        for index in projects:
            demand = Demand.get_info(index)
            tags += demand['tags'] + " "
        print("tag", tags)
        similar_projects = Demand.get_filtered_demands(None, None, None, None, tags, None, None)
        print(similar_projects)
        similar_clients = []
        similar_clients_usernames=[]

        for index in similar_projects:
            if len(similar_clients) == 3:
                break
            demand = Demand.get_info(index)
            if not (demand['client_username'] == username) and not (demand['chosen_developer_username'] == username):
                if demand['client_username'] not in similar_clients_usernames:
                    similar_clients_usernames.append(demand['client_username'])
                    similar_clients.append(User.get_user_info(demand['client_username']))

        return similar_clients

class Developer:
    """
    Developer class. Has methods that inserts to and reads from the Developer table.
    """
    def __init__(self, username):
        df = pd.read_csv('database/Developer.csv')

        df.loc[len(df)] = pd.Series(data=[username, 0, 0, 0, 0, 0],
            index=['username', 'avg_rating', 'avg_given_rating', 'num_of_completed_projects', 'num_of_warnings', 'balance'])
        df.to_csv('database/Developer.csv', index=False)

    @staticmethod
    def get_info(username):
        """
        Returns a dictionary of information for the given developer.
        """
        df = pd.read_csv('database/Developer.csv')
        developer = df.loc[df.username == username]

        return {'username': username,
                'avg_rating': developer['avg_rating'].item(),
                'avg_given_rating': developer['avg_given_rating'].item(),
                'num_of_completed_projects': developer['num_of_completed_projects'].item(),
                'num_of_warnings': developer['num_of_warnings'].item()}

    @staticmethod
    def get_past_projects(username):
        """
        Returns a list of past demands that the developer worked on.
        These past demands are ones that are completed.
        """
        df = pd.read_csv('database/Demand.csv')
        projects = df.loc[(df.chosen_developer_username == username) & (df.is_completed)]

        return projects.index.tolist()

    @staticmethod
    def get_number_of_developers():
        """
        Returns the number of developers in the developer database. Excludes NaNs.
        """
        df = pd.read_csv('database/Developer.csv')
        return df['username'].count() # does not count NaNs

    @staticmethod
    def get_most_active_developers():
        """
        Returns the top 3 developers with the most projects completed.
        """
        df = pd.read_csv('database/Developer.csv')
        sorted_df = df.sort_values(by='num_of_completed_projects', ascending=False)
        sorted_df = sorted_df.iloc[:3]

        usernames = []
        for index, row in sorted_df.iterrows():
            usernames.append(User.get_user_info(row['username']))

        return usernames

    @staticmethod
    def get_similar_developers(username):
        """
        Returns three developers with similar interests as the specified user, based
        on tags of the user's most recent completed projects.
        """
        projects = []
        user_type = User.get_user_info(username)['type_of_user']
        if user_type == 'client':
            projects = Client.get_projects_posted(username)
        else: #is developer
            projects = Developer.get_past_projects(username)
        
        tags = ""
        for index in projects:
            demand = Demand.get_info(index)
            tags += demand['tags'] + " "
        print("tag", tags)
        similar_projects = Demand.get_filtered_demands(None, None, None, None, tags, None, None)
        similar_developers = []
        similar_developers_usernames = []

        for index in similar_projects:
            if len(similar_developers) == 3:
                break
            demand = Demand.get_info(index)
            if not (demand['client_username'] == username) and not (demand['chosen_developer_username'] == username):
                if demand['chosen_developer_username'] not in similar_developers_usernames:
                    similar_developers_usernames.append(demand['chosen_developer_username'])
                    similar_developers.append(User.get_user_info(demand['chosen_developer_username']))

        return similar_developers

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

        hashed = hash_password(password)

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

    @staticmethod
    def get_applicant_info(user_id):
        """
        Returns a dictionary of the applicant's information.
        """
        df = pd.read_csv('database/Applicant.csv')
        user = df.loc[df['user_id'] == user_id]

        if not user.empty:
            return {'user_id': user_id,
                    'first_name': user['first_name'].item(),
                    'last_name': user['last_name'].item(),
                    'email': user['email'].item(),
                    'phone': user['phone'].item(),
                    'credit_card': int(user['credit_card'].item()),
                    'type_of_user': user['type_of_user'].item(),
                    'status': user['status'].item(),
                    'reason': user['reason'].item()}

    @staticmethod
    def is_unique_user_id(user_id):
        """
        Checks whether user_id is unique.
        Returns True if user_id is unique and False if user_id is not unique.
        """
        df0 = pd.read_csv('database/Applicant.csv')
        tmp0 = df0.loc[df0['user_id'] == user_id]

        df1 = pd.read_csv('database/User.csv')
        tmp1 = df1.loc[df1['username'] == user_id]

        df2 = pd.read_csv('database/SuperUser.csv')
        tmp2 = df2.loc[df2['username'] == user_id]

        return tmp0.empty and tmp1.empty and tmp2.empty

    @staticmethod
    def is_unique_email(email):
        """
        Checks whether email is unique.
        Returns True if email is unique and False if email is not unique.
        """
        df0 = pd.read_csv('database/Applicant.csv')
        tmp0 = df0.loc[df0['email'] == email]

        df1 = pd.read_csv('database/User.csv')
        tmp1 = df1.loc[df1['email'] == email]

        df2 = pd.read_csv('database/SuperUser.csv')
        tmp2 = df2.loc[df2['email'] == email]

        return tmp0.empty and tmp1.empty and tmp2.empty

    @staticmethod
    def check_password(user_id, password):
        """
        Checks if the password of a user_id match. 
        Returns true if password given matches the password for user_id 
        given and false if the password does not match.
        """
        df = pd.read_csv('database/Applicant.csv')
        user = df.loc[df['user_id'] == user_id]
        if not user.empty:
            pwhash = user['password'].item()
            return pwhash == hash_password(password) 

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


    @staticmethod
    def reject(user_id, reason):
        """
        Reject the applicant. The applicant's status is changed to rejected.
        """
        df = pd.read_csv('database/Applicant.csv')
        user = df.loc[df.user_id == user_id]

        if user['status'].item() == 'pending':
            # update status
            df.loc[df.user_id == user_id, 'status'] = 'rejected'
            df.loc[df.user_id == user_id, 'reason'] = reason
            df.to_csv('database/Applicant.csv', index=False)

class Demand:
    """
    Demand class. Has methods that inserts to, reads from, and modifies Demand table.
    """
    def __init__(self, client_username, title, tags, specifications, bidding_deadline, submission_deadline):
        """
        Create a new demand by adding a row with the information to the Demand table.
        Returns the demand_id, which is the index of the row that was just added.
        """
        df = pd.read_csv('database/Demand.csv')

        now = datetime.datetime.now()
        format = '%m-%d-%Y %I:%M %p'
        date_posted = now.strftime(format)

        df.loc[len(df)] = pd.Series(data=[client_username, date_posted, title, tags, specifications, bidding_deadline, submission_deadline, False],
            index=['client_username', 'date_posted', 'title', 'tags', 'specifications', 'bidding_deadline', 'submission_deadline', 'is_completed'])

        df.to_csv('database/Demand.csv', index=False)

    @staticmethod
    def get_most_recent_demand_id():
        df = pd.read_csv('database/Demand.csv')
        return df.index.values.tolist()[-1]

    @staticmethod
    def get_info(demand_id):
        """
        Returns a dictionary of information for the specified demand.
        """
        df = pd.read_csv('database/Demand.csv')
        demand = df.loc[int(demand_id)]

        now = datetime.datetime.now()
        deadline_passed = datetime.datetime.strptime(demand['bidding_deadline'], '%m-%d-%Y %I:%M %p') < now

        bids = Bid.get_bids_for_demand(demand_id)
        if len(bids) > 0:
            lowest_bid = Bid.get_info(bids[0])['bid_amount']
        else:
            lowest_bid = None

        if not demand.empty:
            return {'client_username': demand['client_username'],
                    'date_posted': demand['date_posted'],
                    'title': demand['title'],
                    'tags': demand['tags'],
                    'specifications': demand['specifications'],
                    'bidding_deadline': demand['bidding_deadline'],
                    'submission_deadline': demand['submission_deadline'],
                    'is_completed': demand['is_completed'],
                    'bidding_deadline_passed': deadline_passed,
                    'chosen_developer_username' : demand['chosen_developer_username'],
                    'min_bid': lowest_bid,
                    'link_to_client': '/user/' + demand['client_username'],
                    'link_to_demand': '/bid/' + str(demand_id)}

    @staticmethod
    def get_all_demands():
        """
        Returns a list of all demands.
        The demands are ordered from most recent to least recent.
        """
        df = pd.read_csv('database/Demand.csv')
        return df.index.tolist()[::-1]

    @staticmethod
    def get_filtered_demands(start_date, end_date, client, client_rating, tags, min_bid, active):
        """
        Returns a list of demands that are filtered.
        The demands are ordered from most recent to least recent.
        """
        filtered = pd.read_csv('database/Demand.csv')
        now = datetime.datetime.now()
        filtered['date_posted'] = pd.to_datetime(filtered['date_posted'])
        filtered['bidding_deadline'] = pd.to_datetime(filtered['bidding_deadline'])

        # filter by date
        if start_date is not None and start_date != '':
            filtered = filtered.loc[filtered.date_posted >= start_date]

        if end_date is not None and end_date != '':
            filtered = filtered.loc[filtered.date_posted <= end_date]

        # filter by client's username
        if client is not None and client != '':
            filtered = filtered.loc[filtered.client_username == client]

        # filter by active status
        if active != False:
            filtered = filtered.loc[(filtered.bidding_deadline > now) & (filtered.is_completed == False)]

        # filter by client_rating
        if client_rating is not None:
            client_df = pd.read_csv('database/Client.csv')
            merged = pd.merge(filtered, client_df, how='left', left_on=['client_username'], right_on=['username'])
            filtered = merged.loc[merged.avg_rating >= client_rating]

        # filter by the minimum bid amount
        if min_bid is not None:
            def lowest_bid(demand_id):
                bids = Bid.get_bids_for_demand(demand_id)
                return float(Bid.get_info(bids[0])['bid_amount']) if len(bids) > 0 else None

            filtered['lowest_bid'] = pd.Series(filtered.index.map(lowest_bid))
            filtered = filtered.loc[(filtered.lowest_bid >= min_bid) | (filtered.lowest_bid.isnull())]

        # filter by tags
        if tags is not None and tags != '':
            # remove punctuation, change words to lowercase
            tags = map(lambda x: x.lower(), re.findall(r'[^\s!,.?":;0-9]+', tags))
            tags = set(tags)

            def has_tag(demand_id):
                demand_tags = map(lambda x: x.lower(), re.findall(r'[^\s!,.?":;0-9]+', Demand.get_info(demand_id)['tags']))
                demand_tags = set(demand_tags)

                # if there is an intersection between the sets, there are matching tags
                return len(tags & demand_tags) > 0

            filtered['has_tag'] = pd.Series(filtered.index.map(has_tag))
            filtered = filtered.loc[filtered.has_tag == True]

        return filtered.sort_values(['date_posted'], ascending=[True]).index.tolist()[::-1]

    @staticmethod
    def choose_developer(demand_id, developer_username, client_username, bid_amount):
        """
        Update the Demand table when a client chooses a developer for a certain demand.
        Also half of the bid amount is transferred from the client to the developer.
        """
        df = pd.read_csv('database/Demand.csv')
        df.loc[int(demand_id), 'chosen_developer_username'] = developer_username
        df.to_csv('database/Demand.csv', index=False)

        # notify the developer that he/she was chosen to implement the system
        demand_title = Demand.get_info(demand_id)['title']
        message = 'Congratulations! You were chosen by {} for the {} demand.'.format(client_username, demand_title)
        Notification(developer_username, client_username, message)

        # transfer money from client to developer
        Transaction(developer_username, client_username, float(bid_amount) / 2)

class Bid:
    """
    Bid class. Has methods that inserts to Bid table.
    """
    def __init__(self, demand_id, developer_username, bid_amount):
        df = pd.read_csv('database/Bid.csv')
        now = datetime.datetime.now()
        format = '%m-%d-%Y %I:%M %p'
        date_bidded = now.strftime(format)
        bid_amount = round(bid_amount, 2)

        df.loc[len(df)] = pd.Series(data=[demand_id, developer_username, bid_amount, date_bidded],
            index=['demand_id', 'developer_username', 'bid_amount', 'date_bidded'])
        df.to_csv('database/Bid.csv', index=False)

        # send notification to client who made the demand stating that a bid was made
        demand_info = Demand.get_info(demand_id)
        client_username = demand_info['client_username']
        demand_title = demand_info['title']
        message = '{} made a bid of ${} on your {} demand'.format(developer_username, bid_amount, demand_title) 
        Notification(client_username, developer_username, message)

    @staticmethod
    def get_info(bid_id):
        """
        Returns a dictionary of information for the bid specified by the given index.
        Argument bid_id is the index of the row for the bid in the Bid table.
        """
        df = pd.read_csv('database/Bid.csv')
        bid = df.loc[int(bid_id)]

        # get time since bid was made
        now = datetime.datetime.now()
        bid_made = datetime.datetime.strptime(bid['date_bidded'], '%m-%d-%Y %I:%M %p')
        time_diff = now - bid_made

        if time_diff.days > 0:
            td = str(time_diff.days) + 'd'
        else:
            seconds = time_diff.seconds

            if seconds // 3600 > 0:
                td = str(seconds // 3600) + 'h'
            else:
                td = str(seconds // 60) + 'm'

        return {'demand_id': bid['demand_id'],
                'developer_username': bid['developer_username'],
                'bid_amount': format(bid['bid_amount'], '.2f'),
                'time_diff': td}

    @staticmethod
    def get_bids_for_demand(demand_id):
        """
        Returns a list of bid_ids or indexes where the bids are located in the Bid table.
        The list is sorted from lowest bid to highest bid.
        """
        df = pd.read_csv('database/Bid.csv')
        bids = df.loc[df['demand_id'] == int(demand_id)].sort_values(['bid_amount'], ascending=[True])

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
    def __init__(self, username, password, first_name, last_name):
        df = pd.read_csv('database/SuperUser.csv')

        hashed = hash_password(password)
        df.loc[len(df)] = pdf.Series(data=[username, hashed],
            index=['username', 'password'])
    
    # def hash_password(self, password):
    #     """
    #     Returns the hash of the given password.
    #     """
    #     hash_object = hashlib.sha256(password.encode())
    #     return hash_object.hexdigest()

    @staticmethod
    def get_superuser_info(username):
        """
        Returns a dictionary of the superuser's information.
        """
        df = pd.read_csv('database/SuperUser.csv')
        user = df.loc[df['username'] == username]

        if not user.empty:
            return {'id': user['id'],
                    'username': username,
                    'first_name': user['first_name'].item(),
                    'last_name': user['last_name'].item(),
                    'email': user['email'].item()}
    
    @staticmethod
    def check_password(username, password):
        """
        Checks if the password of a user_id match. 
        Returns true if password given matches the password for user_id 
        given and false if the password does not match.
        """
        df = pd.read_csv('database/SuperUser.csv')
        user = df.loc[df['username'] == username]
        if not user.empty:
            pwhash = user['password'].item()
            return pwhash == hash_password(password) 

class Notification:
    """
    Notifications that show up on dashboard.
    """
    def __init__(self,recipient,sender,message):
        df = pd.read_csv('database/Notification.csv')

        now = datetime.datetime.now()
        format = '%m-%d-%Y %I:%M %p'
        date_sent = now.strftime(format)
        
        df.loc[len(df)] = pd.Series(data=[len(df), recipient, sender, date_sent, message, False],
            index=['message_id','recipient', 'sender','date_sent', 'message', 'read_status'])

        df.to_csv('database/Notification.csv', index=False)

    @staticmethod
    def get_number_of_unread(recipient):
        """
        Gets the number of unread messages the recipient username has.
        """
        df = pd.read_csv('database/Notification.csv')
        msgs = df.loc[(df['recipient'] == recipient) & (df.read_status == False)]

        return len(msgs)

    @staticmethod
    def get_notif_to_recipient(recipient, number):
        """
        Get messages to a certain recipient. The amount that is returned is number.
        The most recent notifications are returned.
        """
        df = pd.read_csv('database/Notification.csv')
        msgs = df.loc[df['recipient'] == recipient]
        msgs_sorted = msgs.sort_values(by="message_id", ascending=False) # latest notif first

        notifs = []
        for index, row in msgs_sorted.iterrows():
            if len(notifs) == number :
                break
            temp = { 'sender': row['sender'],
                    'message': row['message'],
                    'date_sent': row['date_sent'],
                    'read_status': row['read_status']}
            notifs.append(temp)
        return notifs

    @staticmethod
    def get_all_notif_to_recipient(recipient):
        """
        Get all notifications to a user
        """
        df = pd.read_csv('database/Notification.csv')
        msgs = df.loc[df['recipient'] == recipient]
        msgs_sorted = msgs.sort_values(by="message_id", ascending=False) # latest notif first

        df.loc[df['recipient'] == recipient, ['read_status']] = True
        df.to_csv('database/Notification.csv', index=False)

        notifs = []
        for index, row in msgs_sorted.iterrows():
            temp = {'sender': row['sender'],
                    'message': row['message'],
                    'date_sent': row['date_sent'],
                    'read_status': row['read_status']}
            notifs.append(temp)
        return notifs

class Warning:
    """
    A warning that is issued to a user

    The status of a warning may be:
        active
        protested
        inactive
    """
    def __init__(self,recipient,status):
        df = pd.read_csv('database/Warning.csv')
        # Create a new row in table for warning
        df.loc[len(df)] = pd.Series(data=[len(df), recipient, status],
            index=['warning_id','warned_user','status'])
        df.to_csv('database/Warning.csv', index=False)


    @staticmethod
    def removeWarning(warning_id):
        """
        Remove warning that user has protested
        """
        df = pd.read_csv('database/Warning.csv')
        # Set warning back to active and give reason
        df.loc[df.warning_id == warning_id, 'status'] = 'inactive'
        df.to_csv('database/Warning.csv', index=False)

    @staticmethod
    def keepWarning(warning_id, reason):
        """
        Keep the warning that user has protested and provide reason for doing so
        """
        df = pd.read_csv('database/Warning.csv')
        # Set warning back to active and give reason
        df.loc[df.warning_id == warning_id, 'status'] = 'active'
        df.loc[df.warning_id == warning_id, 'reason'] = reason
        df.to_csv('database/Warning.csv', index=False)

class Transaction:
    """
    Transactions between users (sender and recipient).
    """
    def __init__(self, recipient, sender, amount, message=None):
        df = pd.read_csv('database/Transaction.csv')
        df.loc[len(df)] = pd.Series(data=[len(df), recipient, sender, amount, 'pending', message],
            index=['transaction_id', 'recipient','sender','amount','status', 'optional_message'])
        df.to_csv('database/Transaction.csv', index=False)

