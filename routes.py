from flask import Flask, render_template

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
	return render_template("profile.html")

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

