from flask import Flask, flash, render_template, request, session, redirect, url_for
import numpy as np
from csv import reader
import datetime
from dateutil import parser
from forms import SignupForm, LoginForm, DemandForm, BidForm, ApplicantApprovalForm, BecomeUserForm, JustifyDeveloperChoiceForm, ProtestForm, ProtestApprovalForm, SubmitSystemForm, RatingForm,RatingMessageForm, TransactionApprovalForm, DeleteAccountForm
from models import User, Client, Developer, Applicant, Demand, Bid, BlacklistedUser, SuperUser, SystemWarning, Notification, Rating, Transaction, DeleteRequest
import helpers

app = Flask(__name__)
app.secret_key = 'development-key'


@app.route("/")
def index():
    number_of_clients = Client.get_number_of_clients()
    number_of_developers = Developer.get_number_of_developers()
    # clients with the most projects
    top_clients = Client.get_clients_with_most_projects()
    # developers making the most money
    top_devs = Developer.get_top_earners()
    return render_template("index.html",number_of_clients=number_of_clients, 
                            number_of_developers=number_of_developers,
                            top_clients = top_clients,
                            top_devs = top_devs)

@app.route("/dashboard")
def dashboard():
    """
    The '/dashboard' route directs a user to view their dashboard.
    """
    if 'username' in session:
        info = User.get_user_info(session['username'])
        if (info == None):
            return render_template("dashboard.html", first_name=" ")
        first_name = info['first_name']

        # Get notifications for this user.
        unread = Notification.get_number_of_unread(session['username'])
        notifications = Notification.get_notif_to_recipient(session['username'], 5)

        # If the user has no projects in history, they are a new user.
        user_type = User.get_user_info(session['username'])['type_of_user']
        recs = {"client_rec_des": "Most Active Clients", 
                "dev_rec_des": "Most Active Developers",
                "client_rec": Client.get_most_active_clients(), 
                "dev_rec": Developer.get_most_active_developers()}

        if user_type == 'client':
            if Client.get_info(session['username'])['num_of_completed_projects'] > 0:
                recs = {"client_rec_des": "Clients with Similar Interests", 
                    "dev_rec_des": "Developers with Similar Interests",
                    "client_rec": Client.get_similar_clients(session['username']), 
                    "dev_rec": Developer.get_similar_developers(session['username'])}
        elif user_type == 'developer':
            if Developer.get_info(session['username'])['num_of_completed_projects'] > 0:
                recs = {"client_rec_des": "Clients with Similar Interests", 
                    "dev_rec_des": "Developers with Similar Interests",
                    "client_rec": Client.get_similar_clients(session['username']), 
                    "dev_rec": Developer.get_similar_developers(session['username'])}
        return render_template("dashboard.html", first_name=first_name, notifications=notifications,
                                recs=recs, unread=unread)
    else:
        return redirect(url_for('login'))

@app.route("/dashboard/projects")
def my_projects():
    """
    The '/dashboard/projects' route directs a user to view their projects.
    """
    user_type = User.get_user_info(session['username'])['type_of_user']
    current = list(Demand.get_info(x) for x in Demand.get_current_projects(session['username']))
    mid = []
    completed = []
    if user_type == "developer":
        bids_by_username = Bid.get_bids_by_username(session['username'])
        temp = []

        for i in bids_by_username:
            info = Bid.get_info(i)['demand_id']
            if info not in temp:
                temp.append(info)

        mid = list(Demand.get_info(y) for y in temp)
        completed = list(Demand.get_info(x) for x in Developer.get_past_projects(session['username']))
    else:
        temp = (Demand.get_info(x) for x in Demand.get_filtered_demands(None, None, session['username'], None, None, None, True))
        for demand in temp:
            if demand['chosen_developer_username'] is np.nan:
                mid.append(demand)
        completed = list(Demand.get_info(x) for x in Client.get_past_projects(session['username']))

    return render_template("myProjects.html", user_type = user_type, current=current, mid=mid, completed=completed)

@app.route("/dashboard/notifications")
def view_notifications():
    """
    The '/dashboard/notifications' route directs a user to view their notifications.
    """
    if 'username' in session:
        unread = Notification.get_number_of_unread(session['username'])
        notifications = Notification.get_all_notif_to_recipient(session['username'])
        return render_template('notifications.html', notifications=notifications, unread=unread)
    else:
        return redirect(url_for('login'))

@app.route("/dashboard_applicant", methods=["GET", "POST"])
def dashboard_applicant():
    """
    The 'dashboard_applicant' route directs an applicant to their dashboard. 
    They can view the status of their application here.
    """
    if session['username']:
        form = BecomeUserForm()
        info = Applicant.get_applicant_info(session['username'])

        if session['type_of_user'] == 'applicant' and request.method == 'GET':
            return render_template("dashboard_applicant.html", info=info, form=form)
        if session['type_of_user'] == 'applicant' and request.method == 'POST':
            info = Applicant.get_applicant_info(session['username'])
            if form.use_prev_credentials.data == 'yes':
                User.use_old_credentials(info['user_id'],info['email'])
                session['type_of_user'] = 'user'
                session['role'] = info['type_of_user']
                # Create a new client or developer in database depending on type of user
                if info['type_of_user'] == 'client':
                    Client(info['user_id'])
                elif info['type_of_user'] == 'developer':
                    Developer(info['user_id'])
                return redirect(url_for('dashboard'))

            elif form.validate():
                User.set_credentials(form.username.data,form.password.data,info['email'])
                session['username'] = form.username.data
                session['type_of_user'] = 'user'
                session['role'] = info['type_of_user']
                # Create a new client or developer in database depending on type of user
                if info['type_of_user'] == 'client':
                    Client(form.username.data)
                elif info['type_of_user'] == 'developer':
                    Developer(form.username.data)
                return redirect(url_for('dashboard'))
            else:
                flash('Login credentials are invalid. Please check that all fields are filled correctly.')
                return render_template("dashboard_applicant.html", info=info, form=form)
        elif session['type_of_user'] == 'user':
            return redirect(url_for('dashboard'))
        elif session['type_of_user'] == 'superuser':
            return redirect(url_for('dashboard_superuser'))

    else:
        return render_template("index.html")

@app.route("/dashboard_superuser")
def dashboard_superuser():
    """
    The 'dashboard_superuser' route directs a superuser to their dashboard.
    """
    if session['username']:
        info = SuperUser.get_superuser_info(session['username'])
        pending_applicants = Applicant.get_pending_applicants()
        protests = SystemWarning.get_protests()
        pending_transactions = Transaction.get_pending_transactions()
        return render_template("dashboard_superuser.html", info=info, pending_applicants=pending_applicants, protests=protests, pending_transactions=pending_transactions)
    else:
        return render_template("index.html")

@app.route("/browse")
def browse():
    """
    The '/browse' route directs anyone on the website to a page where they can browse the 
    demands in the system.
    """
    start_date = request.args.get('start_date', default=None, type=str)
    end_date = request.args.get('end_date', default=None, type=str)
    client = request.args.get('client', default=None, type=str)

    client_rating = None
    for i in range(1,5):
        if request.args.get('rating' + str(i)) == 'on':
            client_rating = i
            break

    tags = request.args.get('tags', default=None, type=str)
    min_bid = request.args.get('min_bid', default=None, type=float)
    active = request.args.get('show_active', default=False)

    demands = Demand.get_filtered_demands(start_date=start_date,
                                          end_date=end_date,
                                          client=client,
                                          client_rating=client_rating,
                                          tags=tags,
                                          min_bid=min_bid,
                                          active=active)
    demands_info = []
    for demand in demands:
        demands_info.append(Demand.get_info(demand))

    return render_template("browse.html", demands_info=demands_info)

@app.route("/user/<name>")
def user(name):
    """
    The '/user/<name>' route directs a user to the profile page of the user with the username
    of [name].
    """
    # if User.has_user_id(name):
    # get basic info
    info = User.get_user_info(name)

    if info['type_of_user'] == 'client':
        rating = Client.get_info(name)['avg_rating']
        projects = Client.get_projects_posted(name)
    elif info['type_of_user'] == 'developer':
        rating = Developer.get_info(name)['avg_rating']
        projects = Developer.get_past_projects(name)

    projects_info = []

    for demand_id in projects:
        projects_info.append(Demand.get_info(demand_id))

    # round rating to the nearest 0.5
    rating = round(0.5 * round(float(rating) / 0.5), 1)
    has_half_star = rating % 1 == .5

    return render_template("profile.html", info=info, rating=int(rating), half_star=has_half_star, projects=projects_info)

@app.route("/apply", methods=["GET", "POST"])
def apply():
    """
    The '/apply route directs a user that is not logged in to the application page.
    """

    # If the user is logged into the system, direct them to their dashboard
    if 'username' in session:
        if session['type_of_user'] == 'user':
            return redirect(url_for('dashboard'))
        if session['type_of_user'] == 'applicant':
            return redirect(url_for('dashboard_applicant'))
        if session['type_of_user'] == 'superuser':
            return redirect(url_for('dashboard_superuser'))
        
    form = SignupForm()

    if request.method == 'POST':
        if form.validate():
            new_user = Applicant(form.role.data, form.first_name.data, form.last_name.data, form.email.data, form.phone.data,
                            form.credit_card.data, form.user_id.data, form.password.data)
            session['username'] = form.user_id.data
            session['type_of_user'] = 'applicant'
            session['role'] = form.role.data
            return redirect(url_for('dashboard_applicant'))
        else:
            flash('Applicant submission is invalid. Please check that all fields are filled correctly.')
            return render_template('application.html', form=form)
    elif request.method == 'GET':
        return render_template('application.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """
    The '/login' route directs the user to the login page if they are not already logged in.
    """

    # If the user is logged into the system, direct them to their dashboard

    if 'username' in session:
        if session['type_of_user'] == 'user':
            return redirect(url_for('dashboard'))
        if session['type_of_user'] == 'applicant':
            return redirect(url_for('dashboard_applicant'))
        if session['type_of_user'] == 'superuser':
            return redirect(url_for('dashboard_superuser'))

    form = LoginForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        # Check if username exists and if password matches
        if BlacklistedUser.is_blacklisted(username):
            session['username'] = username
            return redirect(url_for('blacklist'))
        if User.check_password(username, password):
            session['username'] = username
            session['role'] = User.get_user_info(username)['type_of_user']
            session['type_of_user'] = 'user'
            if SystemWarning.should_be_blacklisted(username):
                BlacklistedUser(username)
                return redirect(url_for('blacklist'))
            return redirect(url_for('dashboard'))
        if Applicant.check_password(username, password):
            session['username'] = username
            session['type_of_user'] = 'applicant'
            return redirect(url_for('dashboard_applicant'))
        if SuperUser.check_password(username, password):
            session['username'] = username
            session['type_of_user'] = 'superuser'
            return redirect(url_for('dashboard_superuser'))

        # If username or password is invalid, notify user
        else:
            flash('Invalid username or password.')
            return render_template('login.html', form=form)

    elif request.method == 'GET':
        return render_template('login.html', form=form)
    
    return render_template('login.html', form=form)

@app.route("/logout")
def logout():
    """
    The '/logout' route will remove the user from the current session if there is one.
    """
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('index'))

@app.route("/blacklist")
def blacklist():
    if 'username' in session:
        info = BlacklistedUser.get_info(session['username'])
        return render_template('blacklist.html', info=info)

    return redirect(url_for('index'))


@app.route("/warnings/<warning_id>/protest", methods=['GET', 'POST'])
def protestWarning(warning_id):
    """
    The /warnings/<warning_id>/protest route directs the user to a page that allows them to protest
    a warning
    """

    # Only allow access to protest warning if regular user
    warning_id = int(warning_id)
    if session['type_of_user'] == 'superuser':
        return redirect(url_for('dashboard_superuser'))
    elif session['type_of_user'] == 'applicant':
        return redirect(url_for('dashboard_applicant')) 

    # User can only protest warning if they are the recipient of the warning and it is an active warning
    if session['username'] != SystemWarning.get_warned_user(warning_id) or SystemWarning.get_warning_status(warning_id)!='active':
        return redirect(url_for('dashboard'))
    
    form = ProtestForm()
    if request.method == 'GET':
        return render_template("protestWarning.html", form=form, warning_id=warning_id)
    else:
        if form.validate():
            SystemWarning.protest_warning(warning_id,form.reason.data)
            return redirect(url_for('dashboard'))
        else:
            return render_template('protestWarning.html', form=form, warning_id=warning_id)

@app.route("/bid/<demand_id>", methods=['GET', 'POST'])
def bidInfo(demand_id):
    """
    The '/bid/<demand_id>' route directs a user to the page with complete
    specifications for the demand.
    """
    demand_info = Demand.get_info(demand_id)
    client_info = User.get_user_info(demand_info['client_username'])
    bids = Bid.get_bids_for_demand(demand_id)
    bids_info = []
    bidders_info = {}

    if (len(bids) > 0):
        lowest_bid = Bid.get_info(bids[0])['bid_amount']
    else:
        lowest_bid = 'None'

    for bid in bids:
        info = Bid.get_info(bid)
        bids_info.append(info)

        if info['developer_username'] not in bidders_info:
            bidders_info[info['developer_username']] = User.get_user_info(info['developer_username'])
    
    form = BidForm()

    if request.method == 'POST':
        if form.validate():
            Bid(demand_id, session['username'], form.bid_amount.data)
            return redirect(url_for('bidInfo', demand_id=demand_id))
        else:
            return redirect(url_for('bidInfo', demand_id=demand_id))

    elif request.method == 'GET':
        return render_template("bidPage.html", demand_info=demand_info, client_info=client_info, bids_info=bids_info, bidders_info=bidders_info, lowest_bid=lowest_bid, form=form, demand_id=demand_id)

@app.route('/bid/<demand_id>/choose-developer', methods=['GET', 'POST'])
def choose_developer(demand_id):
    """
    The '/bid/<demand_id>/choose-developer' route directs a client to a page
    where he/she can select the developer he/she wants to hire to implement the
    system that was demanded.
    """
    demand_info = Demand.get_info(demand_id)

    bids = Bid.get_bids_for_demand(demand_id)
    bids_info = []
    bidders_info = {}

    for bid in bids:
        info = Bid.get_info(bid)
        bids_info.append(info)

        if info['developer_username'] not in bidders_info:
            username = info['developer_username']
            bidders_info[username] = User.get_user_info(username)
            bidders_info[username]['lowest_bid'] = info['bid_amount']

            rating = Developer.get_info(username)['avg_rating']
            # round rating to the nearest 0.5
            rating = round(0.5 * round(float(rating) / 0.5), 1)
            bidders_info[username]['full_stars'] = int(rating)
            bidders_info[username]['has_half_star'] = rating % 1 == .5

    if request.method == 'POST':
        chosen_developer = request.form['developer']
        session['chosen_developer'] = request.form['developer']

        # if the chosen developer had the lowest bid,
        # update the demand's chosen developer
        if chosen_developer == bids_info[0]['developer_username']:
            # updates the table, notifies the developer, and also starts the transaction request
            Demand.choose_developer(demand_id, chosen_developer, session['username'], bids_info[0]['bid_amount'])
            return render_template("developer_chosen.html")

        # if the chosen developer did not have the lowest bid,
        # the client must provide a reason for choosing this developer
        else:
            return redirect(url_for('justify_developer_choice', demand_id=demand_id))
    if request.method == 'GET':
        return render_template("choose_developer.html", demand_id=demand_id, bidders_info=bidders_info)

@app.route("/bid/<demand_id>/justify-developer", methods=['GET', 'POST'])
def justify_developer_choice(demand_id):
    """
    The '/bid/<demand_id>/justify-developer' route is where the client fills out a form
    to explain his/her reason for choosing a developer who did not offer the lowest bid.
    """
    bids = Bid.get_bids_for_demand(demand_id)
    bids_info = []
    bidders_info = {}

    for bid in bids:
        info = Bid.get_info(bid)
        bids_info.append(info)

        if info['developer_username'] not in bidders_info:
            username = info['developer_username']
            bidders_info[username] = User.get_user_info(username)
            bidders_info[username]['lowest_bid'] = info['bid_amount']

    form = JustifyDeveloperChoiceForm()

    if request.method == 'POST':
        if form.validate():
            Demand.choose_developer(demand_id, session['chosen_developer'], session['username'], bidders_info[session['chosen_developer']]['lowest_bid'], form.reason.data)
            return render_template("developer_chosen.html")
        else:
            return render_template("justify_developer_choice.html", demand_id=demand_id, form=form)
    if request.method == 'GET':
        return render_template("justify_developer_choice.html", demand_id=demand_id, form=form)

@app.route("/bid/<demand_id>/upload-system", methods=['GET', 'POST'])
def upload_system(demand_id):
    """
    The '/bid/<demand_id>/upload-system' route is where the developer can upload the system that
    they have created for a demand they have been chosen for.
    """
    form = SubmitSystemForm()
    demand_info = Demand.get_info(demand_id)
    client = demand_info['client_username']

    if request.method == 'POST':
        if form.validate():
            # will not actually store the file
            # project is now completed
            Developer.submit_system(demand_id, session['username'])
            return redirect(url_for('rating', demand_id=demand_id, recipient=client))
        else:
            return render_template("upload_system.html", demand_id=demand_id, form=form)

    if request.method == 'GET':
        return render_template("upload_system.html", demand_id=demand_id, form=form)

@app.route("/bid/<demand_id>/rating/<recipient>", methods=["GET", "POST"])
def rating(demand_id, recipient):
    """
    The '/bid/<demand_id>/rating/<recipient>' route is where the user can rate another user 
    for a demand they were involved in.
    """
    if 'username' not in session:
        return redirect(url_for('login'))

    demand_info = Demand.get_info(demand_id)

    # make sure the user is authorized to rate the recipient
    if session['role'] == 'developer':
        # developer rates the client, so client is recipient
        if session['username'] != demand_info['chosen_developer_username']:
            return render_template('access_denied.html')
    elif session['role'] == 'client':
        # client rates the developer, so developer is recipient
        if session['username'] != demand_info['client_username']:
            return render_template('access_denied.html')

    if Rating.check_if_valid_rating_form(int(demand_id), recipient, session['username']):
        form = RatingForm()

        if request.method == "GET":
            return render_template("rating.html", form=form, recipient=recipient, demand_id=demand_id)
        elif request.method == "POST":
            # low rating
            if form.rating.data <= 2:
                session['rating'+demand_id] = form.rating.data
                return redirect(url_for('ratingMessage', demand_id=demand_id, recipient=recipient))
            elif form.rating.data == None:
                return render_template('rating.html', form=form, recipient=recipient, demand_id=demand_id)
            else:
                # add to form data
                Rating(demand_id, recipient, session['username'], form.rating.data)

                # if the client gave a good rating to a developer (<= 3)
                # the remaining half of the bid amount gets transferred over to the developer
                if session['role'] == 'client':
                    bid_amount = Demand.get_info(demand_id)['chosen_bid_amount']
                    Transaction(recipient, session['username'], round(bid_amount / 2, 2))

                    # update developer's earnings
                    Developer.add_earnings(recipient, bid_amount)

                return render_template('ratingFinished.html', recipient=recipient)
    return render_template('access_denied.html')

@app.route("/bid/<demand_id>/rating/<recipient>/message", methods=["GET", "POST"])
def ratingMessage(demand_id, recipient):
    """
    The '/bid/<demand_id>/rating/<recipient>/message' route directs the user to explain their
    rating if it is below a certain amount.
    """
    if 'username' not in session:
        return redirect(url_for('login'))

    if 'username' in session and ('rating'+demand_id) in session:
        form = RatingMessageForm()
        if request.method == "GET":
            return render_template("ratingMessage.html", form=form, demand_id=demand_id, recipient=recipient)
        elif request.method == "POST":
            if form.message.validate(form):
                Rating(demand_id, recipient, session['username'], session['rating'+demand_id],form.message.data)
                del session['rating'+demand_id]
                return render_template('ratingFinished.html', recipient=recipient)
            else:
                return render_template("ratingMessage.html", form=form, demand_id=demand_id, recipient=recipient)
    return render_template('access_denied.html')

@app.route("/createDemand", methods=['GET', 'POST'])
def createDemand():
    """
    The '/createDemand' route directs a client to the form where he/she can
    create and post a demand on the Turk System.
    """
    if 'username' not in session:
        return redirect(url_for('login'))

    if session['role'] != 'client':
        return render_template('access_denied.html')

    form = DemandForm()

    if request.method == 'POST':
        if form.validate():
            format = '%m-%d-%Y %I:%M %p'
            dt_bid = form.bidding_deadline.data.strftime(format)
            dt_submit = form.submission_deadline.data.strftime(format)

            Demand(session['username'], form.title.data, form.tags.data,
                                form.specifications.data, dt_bid, dt_submit)
            new_demand_id = Demand.get_most_recent_demand_id()

            return redirect(url_for('bidInfo', demand_id=new_demand_id))
        else:
            return render_template('createDemand.html', form=form)
    elif request.method == 'GET':
        return render_template('createDemand.html', form=form)

@app.route("/applicant_approval/<applicant_id>", methods=["GET", "POST"])
def applicant_approval(applicant_id):
    """
    The '/applicant_approval/<applicant_id>' route directs a superuser to approve an application with
    the id of [applicant_id].
    """
    if session['type_of_user'] == 'user':
        return redirect(url_for('dashboard'))
    if session['type_of_user'] == 'applicant':
        return redirect(url_for('dashboard_applicant'))

    form = ApplicantApprovalForm()
    info = Applicant.get_applicant_info(applicant_id)

    if request.method == 'GET':
        return render_template("applicant_approval.html", applicant_id=applicant_id, info=info, form=form)

    if request.method == 'POST':
        if form.decision.data == 'approve':
           Applicant.approve(applicant_id)
           return redirect(url_for('dashboard_superuser'))
        else:
            if form.validate():
                Applicant.reject(applicant_id,form.reason.data)
                return redirect(url_for('dashboard_superuser'))
            else:
                flash('Approval form is invalid. Please make sure all fields are completed correctly')
                return render_template("applicant_approval.html", applicant_id=applicant_id, info=info, form=form)

@app.route("/protest_approval/<warning_id>", methods=["GET", "POST"])
def protest_approval(warning_id):
    """
    The '/protest_approval/<warning_id>' route directs a superuser to approve a protest against a warning
    with the id of [warning_id].
    """
    if session['type_of_user'] == 'user':
        return redirect(url_for('dashboard'))
    if session['type_of_user'] == 'applicant':
        return redirect(url_for('dashboard_applicant'))

    warning_id = int(warning_id)
    info = SystemWarning.get_warning_info(warning_id)
    username = info['warned_user']
    type_of_user = User.get_user_info(username)['type_of_user']
    avg_rating = 0
    if type_of_user == 'client':
        avg_rating = Client.get_info(username)['avg_rating']
    elif type_of_user == 'developer':
        avg_rating = Developer.get_info(username)['avg_rating']

    form = ProtestApprovalForm()

    if request.method == 'GET':
        return render_template("protestApproval.html", warning_id=warning_id, info=info, form=form, avg_rating=avg_rating)
    if request.method == 'POST':
        if form.validate():
            if form.decision.data == 'remove':
                SystemWarning.remove_warning(warning_id)
                Notification(username,session['username'],'Your protest for warning#'+ str(warning_id) +' was approved. Your warning has been deleted.')
            else:
                SystemWarning.keep_warning(warning_id)
                Notification(username,session['username'],'Your protest for warning#'+ str(warning_id) +' was not approved. Your warning remains.')
            return redirect(url_for('dashboard_superuser'))
        else:
            return render_template("protestApproval.html", warning_id=warning_id, info=info, form=form, avg_rating=avg_rating)

@app.route("/transaction_approval/<transaction_id>", methods=["GET", "POST"])
def transaction_approval(transaction_id):
    """
    The '/transaction_approval/<transaction_id>' route directs a superuser to approve a transaction with
    the id of [transaction_id].
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    if session['type_of_user'] == 'user':
        return redirect(url_for('dashboard'))
    if session['type_of_user'] == 'applicant':
        return redirect(url_for('dashboard_applicant'))

    form = TransactionApprovalForm()
    info = Transaction.get_transaction_info(transaction_id)
    transaction_id = int(transaction_id)

    if request.method == 'GET':
        enough_money = User.does_user_have_enough_money(info['sender'],int(info['amount']))
        return render_template("transactionApproval.html", form=form, transaction_id=transaction_id,info=info,enough_money=enough_money)
    if request.method == 'POST':
        if form.validate():
            if form.decision.data == 'approve':
                Transaction.approve_transaction(transaction_id)
                Notification(info['sender'],session['username'],'Your transaction (Transaction#'+ str(transaction_id) +') was approved.')
            else:
                Transaction.deny_transaction(transaction_id)
                Notification(info['sender'],session['username'],'Your transaction (Transaction#'+ str(transaction_id) +') was denied.')
                SystemWarning(info['sender'],'active')
            return redirect(url_for('dashboard_superuser'))
        else:
            return render_template("protestApproval.html", warning_id=warning_id, info=info, form=form, avg_rating=avg_rating)

@app.route("/warnings")
def warning():
    """
    The '/warnings' route directs a user to view all their warnings.
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    if session['type_of_user'] == 'superuser':
        return redirect(url_for('dashboard_superuser'))
    if session['type_of_user'] == 'applicant':
        return redirect(url_for('dashboard_applicant'))
    username = session['username']
    warnings = SystemWarning.get_user_warnings(username)
    return render_template("warnings.html", warnings=warnings)

@app.route("/deleteAccount", methods=["GET", "POST"])
def deleteAccount():
    """
    The '/deleteAccount' route directs a user to a form where they can request the superuser
    to delete their account.
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    if session['type_of_user'] == 'superuser':
        return redirect(url_for('dashboard_superuser'))
    if session['type_of_user'] == 'applicant':
        return redirect(url_for('dashboard_applicant'))
    form = DeleteAccountForm()

    if request.method == 'GET':
        return render_template("deleteAccount.html",form=form)
    else:
        if form.validate():
            if form.delete.data:

                return redirect(url_for('dashboard_superuser'))
            else:
                return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)
