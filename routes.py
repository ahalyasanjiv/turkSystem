from flask import Flask, render_template, request, session
from csv import reader
from models import User, Client, Developer, Applicant, Demand, Bid, BlacklistedUser, SuperUser

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/browse")
def browse():
    return render_template("browse.html")

@app.route("/user/<name>")
def user(name):
    info = User.get_user_info(name)

    return render_template("profile.html", username=name, first_name=info['first_name'],
        last_name=info['last_name'], email=info['email'], phone=info['phone'],
        type_of_user=info['type_of_user'], about=info['about'])

@app.route("/apply")
def apply():
	return render_template("application.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	""" 
	The "/login" route will direct users to the login page if they are not logged in. 
	If the user is already logged in, they will be redirected to their dashboard.
	"""
	# If user is already logged in, redirect them to dashboard
	if 'username' in session:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if request.method == 'POST' and form.validate():
    	username = form.username.data
        password = form.password.data
        user_exists = False
        with open('/database/User.csv', 'r') as f:
        	csvreader = reader(f, delimiter=',')
        	for row in csvreader:
       			if username in row[1]:
       				user_exists = True
       	

    	

	return render_template("login.html")

@app.route("/logout")
def logout():
    """
    The '/logout' will remove the user from the current session."""
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

