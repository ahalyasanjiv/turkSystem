from flask import Flask, flash, render_template, request, session, redirect, url_for
from csv import reader
import datetime
from models import User, Client, Developer, Applicant, Demand, Bid, BlacklistedUser, SuperUser
from forms import SignupForm, LoginForm

app = Flask(__name__)
app.secret_key = 'development-key'


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

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
        return redirect(url_for('dashboard'))

    form = SignupForm()

    if request.method == 'POST':
        if form.validate():
            new_user = Applicant(form.role.data, form.first_name.data, form.last_name.data, form.email.data, form.phone.data,
                            form.credit_card.data, form.username.data, form.password.data)
            session['username'] = form.username.data
            session['role'] = form.role.data
            return redirect(url_for('dashboard'))
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
            return redirect(url_for('dashboard'))

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

if __name__ == "__main__":
    app.run(debug=True)
