from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3
import hashlib

# Variables
DATABASE_FILE = "gym-database.db"

app = Flask(__name__)

app.secret_key = "shhsecret"

# Functions
#sqlite3.connect("gym-database.db?mode=WAL", check_same_thread=False)

#function to add a user to database after sign in
def hash_password(password):
    salt = b'some_random_salt'  # You should use a random salt
    password = password.encode('utf-8')
    hashed_password = hashlib.sha256(salt + password).hexdigest()
    return hashed_password

def add_user(table_name, add_name, add_password):
    '''Add items to the database'''
    with sqlite3.connect(DATABASE_FILE) as connection:
        # Connect the cursor
        cursor = connection.cursor()
        # SQL statement 
        sql = f"INSERT INTO {table_name} (name, password) VALUES (?, ?)"
        # Execute the SQL statement
        cursor.execute(sql, (add_name, add_password))
        connection.commit()

def add_lift(username, lift_name, weight, description):
    """Add an Exercise"""
    with sqlite3.connect(DATABASE_FILE) as connection:
        # Connect the cursor
        cursor = connection.cursor()
        # SQL statement to insert the lift data
        sql = "INSERT INTO Excercise (name, weight, description) VALUES (?, ?, ?)"
        cursor.execute(sql, (lift_name, weight, description))
        connection.commit()

        # Retrieve the ID of the added lift
        lift_id = cursor.lastrowid

        # Associate the lift with the user
        user_id_sql = "SELECT id FROM User WHERE name = ?"
        cursor.execute(user_id_sql, (username,))
        user_id = cursor.fetchone()[0]


        # Create a relation between the user and the added lift
        user_lift_relation_sql = "INSERT INTO UserExcercise (user_id, lift_id) VALUES (?, ?)"
        cursor.execute(user_lift_relation_sql, (user_id, lift_id))
        connection.commit()



#searching if a user is in a database
def search(username, password):
    """Check if username and password exist in the database."""
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()
        sql = "SELECT * FROM User WHERE name = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()  # Fetch the first row from the result set
        if user:
            stored_password = user[2]  # Get stored password
            if str(password) == str(stored_password): 
                # User exists and password is correct.
                print("password is correct")
                return True, user[0]  # Return True for authentication and user ID
                
            else:
                print(username,stored_password)
                print("password incorrect")
                return False, None  # Return False for authentication
                
        else:
            print("user doesn't exist")
            return False, None  # Return False for authentication
@app.route('/user/<int:user_id>')
def get_user_id(user_id):
    if "user_id" in session and session["user_id"] == user_id:
        with sqlite3.connect(DATABASE_FILE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM User WHERE id=?', (user_id,))
            user = cursor.fetchone()
            print("User:", user)
            cursor.execute('SELECT * FROM Excercise WHERE user_id=?', (user_id,))
            excercises = cursor.fetchall() 
            print("Exercises:", excercises) 
        return render_template("user.html", user=user, excercises=excercises, title="Dashboard")
    else:
        return redirect(url_for("login"))

        
#connecting the lift id and user id
def user_lift(sql_id, lift_id):
    with sqlite3.connect(DATABASE_FILE) as connection:
        # Connect the cursor
        cursor = connection.cursor()
        # SQL statement
        sql = f"INSERT INTO Excercise (excercise_id, set_id) VALUES (?, ?, ?)"
        cursor.execute(sql, (sql_id, lift_id))
        connection.commit()
    

@app.route("/")
def home():
    return render_template("home.html", title="Home Page")

@app.route("/signup")
def signup():
    return render_template('signup.html', title="Sign in")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        User_Authentication, sql_id = search(username, password)
        print(username, password)
        if User_Authentication == True:
            session["user_id"] = sql_id  # Store the user ID in the session
            print("user authenticated in login function")
            return redirect(url_for("get_user_id", user_id=sql_id))
        else:
            error_message = "Invalid login credentials. Please try again. (usernames and passwords are case sensitive)"
            return render_template("login.html", title="Log in", error=error_message)
    else:
        if "user_id" in session:
            return redirect(url_for("get_user_id", user_id=session["user_id"]))
        return render_template("login.html", title="Log in")

        

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/add_user")
def add_user_route():
    username = request.args.get('username')
    password = request.args.get('password')
    confirm_password = request.args.get('confirm')
    
    with sqlite3.connect(DATABASE_FILE) as connection:
        cursor = connection.cursor()
        sql = "SELECT * FROM User WHERE name = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()  # Fetch the first row from the result set
        if username == user: #checking that username isn't already in the database
            error_message = "Username is taken please use another name"
            return render_template("signup.html", title="Signup in", error_message=error_message)
        if password == confirm_password:
            cursor.execute("INSERT INTO User (name,password) VALUES (?, ?)",(username, password))
            connection.commit
            return render_template("login.html", title="Log in")
        else:
            error_message = "Your confirmed password is incorrect try again"
            return render_template("signup.html", title="Signup in", error_message=error_message)
        

        

    
#creating a way to add excercises to database using the function
@app.route('/add_lift', methods=['GET', 'POST'])
def add_lift_route():
    if 'user_id' in session:
        user_id = session['user_id']  # Get the user's ID from the session

        if request.method == 'POST':
            lift_name = request.form.get('name')
            weight = request.form.get('weight')
            description = request.form.get('description')

            with sqlite3.connect(DATABASE_FILE) as connection:
                cursor = connection.cursor()

                # Insert the Excercise data including the user's ID
                sql = "INSERT INTO Excercise (name, description, weight, user_id) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (lift_name, description, weight, user_id))
                connection.commit()
            return redirect(url_for('get_user_id', user_id=user_id))
        
        return render_template('add_lift.html', title='Add Lift')
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True) 