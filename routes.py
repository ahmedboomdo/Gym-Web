from flask import Flask, render_template
import sqlite3
#preformed all imports

#creating functions
def add_item(table_name, connection, add_name, add_password):
    '''Add items to database'''
    #connect the cursor
    cursor = connection.cursor()
    #SQL statment 
    sql = f"INSERT INTO {table_name} (name, password) VALUES(?,?)"
    #execute the sql statement.
    cursor.execute(sql,(add_name, add_password))
    connection.commit()

with sqlite3.connect(DATABASE_FILE) as connection:
    add_item('User', connection, 'ahmed', '1233824')

app = Flask(__name__)


#creating a route to the homepage
@app.route("/")
def home():
    return render_template("home.html", title = "Home Page")


#creating a route to signup and login pages
@app.route("/signup")
def signup():
    return render_template("signup.html",title = "Sign up")


@app.route("/login")
def login():
    return render_template("login.html",title = "Log in")


if __name__ == '__main__':
    app.run(debug = True)