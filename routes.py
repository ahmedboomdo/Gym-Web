from flask import Flask, render_template
import sqlite3
#preformed all imports

#variables
DATABASE_FILE = "Database\gym-database.db"

#creating functions
def add_user(table_name, connection, add_name, add_password):
    '''Add items to database'''
    #connect the cursor
    cursor = connection.cursor()
    #SQL statment 
    sql = f"INSERT INTO {table_name} (name, password) VALUES(?,?)"
    #execute the sql statement.
    cursor.execute(sql,(add_name, add_password))
    connection.commit()

with sqlite3.connect(DATABASE_FILE) as connection:
    pass

app = Flask(__name__)


#creating a route to the homepage
@app.route("/")
def home():
    return render_template("home.html", title = "Home Page")


#creating a route to signup and login pages
@app.route("/signup", methods = ['POST','GET'])
def signup():
  formstuff = None
  if len(request.args) > 0:
    formstuff = []
    formstuff.append(request.args.get('username'))
    formstuff.append(request.args.get('password'))
  return render_template('about.html', formstuff=formstuff)


@app.route("/login")
def login():
    return render_template("login.html",title = "Log in")

@app.route("/add_data")
def data():
    return render_template("login.html",title = "shhh")


if __name__ == '__main__':
    app.run(debug = True)