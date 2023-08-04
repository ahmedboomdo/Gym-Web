from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3
#preformed all imports

#variables
DATABASE_FILE = "gym-database.db"
form = None

app = Flask(__name__)

app.secret_key = "shhsecret"

#Functions
def add_user(table_name,connection, add_name, add_password):
    '''Add items to database'''
    connection = sqlite3.connect(DATABASE_FILE)
    #connect the cursor
    cursor = connection.cursor()
    #SQL statment 
    sql = f"INSERT INTO {table_name} (name, password) VALUES(?,?)"
    #execute the sql statement.
    cursor.execute(sql,(add_name, add_password))
    connection.commit()


def add_lift( connection, lift_name, weight, description):
    """add a Excercise"""
    connection = sqlite3.connect(DATABASE_FILE)
    #connecting cursor
    cursor = connection.cursor()
    #SQL statement
    sql=f"INSERT INTO Excercise (name, weight, description) VALUES(?,?,?)"
    cursor.execute(sql,(lift_name, weight, description))
    connection.commit()

with sqlite3.connect(DATABASE_FILE) as connection:
    pass






#creating a route to the homepage
@app.route("/")
def home():
    return render_template("home.html", title = "Home Page")


#creating a route to signup and login pages
@app.route("/signup")
def signup():
    return render_template('signup.html',title = "Sign in")


#creating login page route
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user =request.form["nm"]
        session["user"] = user
        return redirect(url_for("user", usr = user))
    else:
        if "user" in session:
            return redirect(url_for("user"))
        return render_template("login.html",title = "Log in")
    
#creating a way of logging out
@app.route ("/logout")
def logout():
    session.pop("user",  None)
    return redirect(url_for("login"))

#ustillizing the add_user function
@app.route("/add_user")
def data():
    username = request.args.get('username')
    password = request.args.get('password')
    add_user("User", connection, username, password)
    return render_template("login.html",title = "Log in")

#creating the dashboard 
@app.route('/user')
def user():
    if "user" in session:
        user = session["user"]
        return f"<h1>{user}<h1>"
    else:
        return redirect(url_for("login"))

    conn = sqlite3.connect(DATABASE_FILE)
    #connect the cursor
    cursor = conn.cursor()
    #SQL statment 
    cursor.execute('SELECT * FROM User where id=?',(id,))
    user = cursor.fetchone()
    return render_template("user.html",user=user, title = "Homepage")

#creating a way to add excercises to database using the function
@app.route("/add_lift")
def lift_data():
    name = request.args.get("name")
    description = request.args.get("description")
    weight = request.args.get("weight")
    add_lift(connection, name, weight, description)
    return render_template("lift.html", title="Add Lift")
    




if __name__ == '__main__':
    app.run(debug = True)