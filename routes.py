from flask import Flask, render_template
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
    active_demands = Demand.get_all_active_demands()

    active_demands_info = []
    for demand in active_demands:
        active_demands_info.append(Demand.get_info(demand))

    return render_template("browse.html", active_demands_info=active_demands_info)

@app.route("/user/<name>")
def user(name):
    info = User.get_user_info(name)

    return render_template("profile.html", info=info)

@app.route("/apply")
def apply():
    return render_template("application.html")

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

