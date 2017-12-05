from flask import Flask, flash, render_template, request, session, redirect, url_for
from csv import reader
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
    active_demands = Demand.get_all_active_demands()
    active_demands_info = []
    
    for demand in active_demands:
        active_demands_info.append(Demand.get_info(demand))

    return render_template("browse.html", active_demands_info=active_demands_info)

@app.route("/user/<name>")
def user(name):
    info = User.get_user_info(name)
    return render_template("profile.html", info=info)

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

@app.route("/bid/<bidName>")
def bidInfo(bidName):
    return render_template("bidPage.html")

@app.route("/createDemand")
def createDemand():
    return render_template("createDemand.html")

if __name__ == "__main__":
    app.run(debug=True)

