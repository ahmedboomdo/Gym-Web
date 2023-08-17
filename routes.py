from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3

# Variables
DATABASE_FILE = "gym-database.db"

app = Flask(__name__)

app.secret_key = "shhsecret"

# Functions

#function to add a user to database after sign in
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
        user_lift_relation_sql = "INSERT INTO UserLifts (user_id, lift_id) VALUES (?, ?)"
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
            # Fetch exercises associated with the user
            cursor.execute('SELECT * FROM Excercise WHERE user_id=?', (user_id,))
            excercises = cursor.fetchall()
        return render_template("user.html", user=user, excercises=excercises, title="Homepage")
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
        print(username,password)
        if User_Authentication == True:
            session["user_id"] = sql_id  # Store the user ID in the session
            print("user authenticated in login function")
            return redirect(url_for("get_user_id"))  # Redirect to user route
            
        else:
            error_message = "Invalid login credentials. Please try again. (usernames and passwords are case senstive)"
            return render_template("login.html", title="Log in", error=error_message)
    else:
        if "user_id" in session:
            return redirect(url_for("get_user_id"))
        return render_template("login.html", title="Log in")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/add_user")
def add_user_route():
    username = request.args.get('username')
    password = request.args.get('password')
    add_user("User", username, password)
    return render_template("login.html", title="Log in")

    
#creating a way to add excercises to database using the function
@app.route('/add_lift', methods=['POST','GET'])
def add_lift_route():
    if 'user_id' in session:  # Check if the user is logged in
        user_id = session['user_id']

        # Extract form data
        lift_name = request.form.get('name')
        weight = request.form.get('weight')
        description = request.form.get('description')

        # Retrieve the username from the database based on the user ID
        with sqlite3.connect(DATABASE_FILE) as connection:
            cursor = connection.cursor()
            username_query = "SELECT name FROM User WHERE id = ?"
            cursor.execute(username_query, (user_id,))
            username = cursor.fetchone()[0]

        # Call the function to add the lift and associate with the user
        add_lift(username, lift_name, weight, description)

        return redirect(url_for('get_user_id', user_id=user_id))  # Redirect to dashboard
    else:
        return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)