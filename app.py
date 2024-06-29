from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "sup"

connection_string = "mongodb+srv://Stravecodes:ASh2LeaVounah7pu@strave.3nqbbea.mongodb.net/?retryWrites=true&w=majority&appName=Strave"
mongo = MongoClient(connection_string)
db = mongo["blaze"]
users = db["users"]
messages = db["messages"]

free_fire = db["free_fire"]
pubg = db["pubg"]
codm = db["codm"]

@app.route("/")
def home():
    if "username" in session:
        return render_template("home.html", uname=session["username"])
    return render_template("index.html")

@app.route("/msg_submit", methods=["POST"])
def msg_sub():
    name = request.form.get("name")
    message = request.form.get("message")
    data = {"name": name, "message": message}
    messages.insert_one(data)
    return redirect(url_for("home"))

@app.route("/login")
def login():
    err = request.args.get("err")
    done = request.args.get("done")
    if 'username' in session:
        return render_template("home.html", uname=session["username"])
    return render_template("login.html", err=err, done=done)

@app.route("/submit_log", methods=["POST"])
def submit_log():
    uname = request.form.get("uname")
    pwd = request.form.get("pwd")
    data = {"username": uname, "password": pwd}
    user = users.find_one(data)
    if user:
        session["username"] = uname
        return redirect(url_for("home"))
    return redirect(url_for("login", err=True))

@app.route("/signup")
def sign_up():
    if "username" in session:
        return render_template("home.html", uname=session["username"])
    err_user_taken = request.args.get("err_user_taken")
    err_pwd_match = request.args.get("err_pwd_match")
    return render_template("register.html", err_user_taken=err_user_taken, err_pwd_match=err_pwd_match)

@app.route("/submit_reg", methods=["POST"])
def submit_reg():
    uname = request.form.get("uname")
    pwd1 = request.form.get("pwd1")
    pwd2 = request.form.get("pwd2")
    email = request.form.get("email")
    phone = request.form.get("phone")

    if pwd1 != pwd2:
        return redirect(url_for("sign_up", err_pwd_match=True))

    if users.find_one({"username": uname}) or users.find_one({"email": email}):
        return redirect(url_for("sign_up", err_user_taken=True))

    data = {
        "username": uname,
        "password": pwd1,
        "email": email,
        "phone": phone
    }

    users.insert_one(data)
    return redirect(url_for("login", done=True))

@app.route("/game/<gamename>")
def game(gamename):
    
    if not "username" in session:
        return redirect(url_for("login"))
    match_collections = {
        "ff": free_fire,
        "pubg": pubg,
        "codm": codm
    }

    if gamename in match_collections:
        match_details = list(match_collections[gamename].find())
    else:
        match_details = []

    return render_template("game.html", gamename=gamename, match_details=match_details, mc=len(match_details))

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/match", methods=["GET", "POST"])
def match():
    if not "username" in session:
        return redirect(url_for("login"))
    if request.method == "GET":
        gamename = request.args.get("gamename")
        return render_template("match.html", gamename=gamename)

    gamename = request.form.get("gamename")
    uid = request.form.get("uid")
    upi_id = request.form.get("upi_id")
    if users.find_one({"uid": uid}):
        return redirect(url_for("sup", err_uid=True))
    username = session.get("username")
    data = {
        "gamename": gamename,
        "uid": uid,
        "upi_id": upi_id,
        "username": username
        }
    session["gamename"] = gamename
    session["uid"] = uid

    session["data"] = data

    return redirect(url_for("pay"))

@app.route("/pay")
def pay():
    if not "username" in session:
        return redirect(url_for("login"))
    return render_template("pay.html")

@app.route("/success")
def success():
    gamename = session.get("gamename")
    uid = session.get("uid")
    if gamename == "ff":
        gamename = "Free Fire"
    elif gamename == "codm":
        gamename = "COD Mobile"
    elif gamename == "pubg":
        gamename = "PUBG"

    data = session.get("data")
    users.insert_one(data)

    return render_template("successful.html", gamename=gamename, uid=uid)

@app.route("/submit_match", methods=["POST"])
def submit_match():
    return render_template("pay.html")

@app.route("/sup")
def sup():
    err = request.args.get("err_uid")
    return render_template("already_exists.html", err=err)

if __name__ == "__main__":
    app.run(debug=True)
