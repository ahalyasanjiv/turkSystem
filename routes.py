from flask import Flask, flash, render_template, request, session, redirect, url_for
import pandas as pd
from csv import reader
import datetime
from models import User, Client, Developer, Applicant, Demand, Bid, BlacklistedUser, SuperUser, Notification
from forms import SignupForm, LoginForm, ApplicantApprovalForm, BecomeUserForm

app = Flask(__name__)
app.secret_key = 'development-key'


@app.route("/")
def index():
    number_of_clients = Client.get_number_of_clients()
    number_of_developers = Developer.get_number_of_developers()
    # clients with the most projects
    top_clients = Client.get_top_clients()
    # developers making the most money
    top_devs =[]
    return render_template("index.html",number_of_clients=number_of_clients, 
                            number_of_developers=number_of_developers,
                            top_clients = top_clients,
                            top_devs = top_devs)

@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        info = User.get_user_info(session['username'])
        if (info == None):
            return render_template("dashboard.html", first_name=" ")
        first_name = info['first_name']

        # Get notifications for this user.
        notifications = Notification.get_notif_to_recipient(session['username'], 5)

        # If the user has no projects in history, they are a new user.
        new_user = True
        user_type = User.get_user_info(session['username'])['type_of_user']

        if user_type == 'client':
            if Client.get_info(session['username'])['num_of_completed_projects'] > 0:
                new_user = False
        else:
            if Developer.get_info(session['username'])['num_of_completed_projects'] > 0:
                new_user = False
        return render_template("dashboard.html", first_name=first_name, notifications=notifications,
                                new_user=new_user)
    else:
        return redirect(url_for('login'))

@app.route("/dashboard/notifications")
def view_notifications():
    if 'username' in session:
        notifications = Notification.get_all_notif_to_recipient(session['username'])
        return render_template('notifications.html', notifications=notifications)
    else:
        return redirect(url_for('login'))

@app.route("/dashboard_applicant", methods=["GET", "POST"])
def dashboard_applicant():
    if session['username']:
        form = BecomeUserForm()
        if session['type_of_user'] == 'applicant' and request.method == 'GET':
            info = Applicant.get_applicant_info(session['username'])
            return render_template("dashboard_applicant.html", info=info, form=form)
        if session['type_of_user'] == 'applicant' and request.method == 'POST':
            info = Applicant.get_applicant_info(session['username'])
            if form.use_prev_credentials.data == 'yes':
                User.use_old_credentials(info['user_id'],info['email'])
                session['type_of_user'] == 'user'
                session['role'] == info['type_of_user']
                return redirect(url_for('dashboard'))
            elif form.validate():
                User.set_credentials(form.username.data,form.password.data,info['email'])
                session['username'] == form.username.data
                session['type_of_user'] == 'user'
                session['role'] == info['type_of_user']
                return redirect(url_for('dashboard'))
            else:
                flash('Login credentials are invalid. Please check that all fields are filled correctly.')
                return render_template("dashboard_applicant.html", info=info, form=form)
        elif session['type_of_user'] == 'user':
            return render_template("dashboard", info=info)
        elif session['type_of_user'] == 'superuser':
            return render_template("dashboard_superuser", info=info)

    else:
        return render_template("index.html")





@app.route("/dashboard_superuser")
def dashboard_superuser():
    if session['username']:
        info = SuperUser.get_superuser_info(session['username'])
        df = pd.read_csv('database/Applicant.csv')
        get_apps = df.loc[df['status'] == 'pending']
        pending_applicants = get_apps['user_id'].values.tolist()
        return render_template("dashboard_superuser.html", info=info, pending_applicants=pending_applicants)
    else:
        return render_template("index.html")

@app.route("/browse")
def browse():
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
    if 'username' in session:
        return redirect(url_for('dashboard_applicant'))

    form = SignupForm()

    if request.method == 'POST':
        if form.validate():
            new_user = Applicant(form.role.data, form.first_name.data, form.last_name.data, form.email.data, form.phone.data,
                            form.credit_card.data, form.user_id.data, form.password.data)
            session['username'] = form.user_id.data
            session['role'] = form.role.data
            return redirect(url_for('dashboard_applicant'))
        else:
            flash('Applicant submission is invalid. Please check that all fields are filled correctly.')
            return render_template('application.html', form=form)


    elif request.method == 'GET':
        return render_template('application.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        username = form.username.data
        password = form.password.data
        # Check if username exists and if password matches
        if User.check_password(username, password):
            session['username'] = username
            session['type_of_user'] = 'user'
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
    return redirect(url_for('index'))

@app.route("/warning/protest")
def protestWarning():
    return render_template("protestWarning.html")

@app.route("/bid/<demand_id>")
def bidInfo(demand_id):
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

    return render_template("bidPage.html", demand_info=demand_info, client_info=client_info, bids_info=bids_info, bidders_info=bidders_info, lowest_bid=lowest_bid)

@app.route("/createDemand")
def createDemand():
    return render_template("createDemand.html")

@app.route("/applicant_approval/<applicant_id>", methods=["GET", "POST"])
def applicant_approval(applicant_id):
    if session['type_of_user'] == 'user':
        return redirect(url_for('dashboard'))
    # if session['type_of_user'] == 'applicant':
        # return redirect(url_for('dashboard_applicant'))

    form = ApplicantApprovalForm()

    if request.method == 'GET':
        info = Applicant.get_applicant_info(applicant_id)
        return render_template("applicant_approval.html", applicant_id=applicant_id, info=info, form=form)

    if request.method == 'POST':
        if form.accept.data == True:
            Applicant.approve(applicant_id)
        else:
            Applicant.reject(applicant_id)

        return redirect(url_for('dashboard_superuser'))

if __name__ == "__main__":
    app.run(debug=True)
