from flask import Flask, render_template, request
import sqlite3
#preformed all imports

#variables
DATABASE_FILE = "Database\gym-database.db"
form = None

#creating functions
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

with sqlite3.connect(DATABASE_FILE) as connection:
    pass

app = Flask(__name__)


#creating a route to the homepage
@app.route("/")
def home():
    return render_template("home.html", title = "Home Page")


#creating a route to signup and login pages
@app.route("/signup")
def signup():
    return render_template('signup.html',title = "Sign in")



@app.route("/login")
def login():
    return render_template("login.html",title = "Log in")

@app.route("/add_user")
def data():
    username = request.args.get('username')
    password = request.args.get('password')
    print(username, password, connection)
    add_user("User", connection, username, password)
    return render_template("login.html",title = "Log in")

@app.route('/user/<int:id>')
def user(id):
    conn = sqlite3.connect(DATABASE_FILE)
    #connect the cursor
    cursor = conn.cursor()
    #SQL statment 
    cursor.execute('SELECT * FROM user where id=?',(id,))
    user = cursor.fetchone()

    #sql = ('SELECT name FROM user where id=?'(id))
    #execute the sql statement.
    #cursor.execute(sql,())
    #connection.commit()
    return render_template("user.html",user=user, title = "Homepage")

if __name__ == '__main__':
    app.run(debug = True)