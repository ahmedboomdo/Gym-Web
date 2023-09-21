from flask import Flask, render_template, redirect, request, session, url_for
import sqlite3

# Variables
database_file = "gym-database.db"

app = Flask(__name__)
app.secret_key = "shhsecret"


# Functions
def add_user(table_name, add_name, add_password):
    """Add items to the database."""
    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()
        sql = f"INSERT INTO {table_name} (name, password) VALUES (?, ?)"
        cursor.execute(sql, (add_name, add_password))
        connection.commit()


def add_lift(username, lift_name, weight, description):
    """Add an exercise."""
    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()
        sql = "INSERT INTO Exercise (name, weight, description) VALUES (?, ?, ?)"
        cursor.execute(sql, (lift_name, weight, description))
        connection.commit()

        lift_id = cursor.lastrowid
        user_id_sql = "SELECT id FROM User WHERE name = ?"
        cursor.execute(user_id_sql, (username,))
        user_id = cursor.fetchone()[0]

        user_lift_relation_sql = "INSERT INTO UserExercise (user_id, lift_id) VALUES (?, ?)"
        cursor.execute(user_lift_relation_sql, (user_id, lift_id))
        connection.commit()


def search(username, password):
    """Check if username and password exist in the database."""
    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()
        sql = "SELECT * FROM User WHERE name = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        if user:
            stored_password = user[2]
            if str(password) == str(stored_password):
                print("Password is correct")
                return True, user[0]
            else:
                print(username, stored_password)
                print("Password incorrect")
                return False, None
        else:
            print("User doesn't exist")
            return False, None


@app.route('/user/<int:user_id>')
def get_user_id(user_id):
    if "user_id" in session and session["user_id"] == user_id:
        with sqlite3.connect(database_file) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM User WHERE id=?', (user_id,))
            user = cursor.fetchone()
            print("User:", user)

            cursor.execute('SELECT * FROM Exercise WHERE user_id=?', (user_id,))
            exercises = cursor.fetchall()
            print("Exercises:", exercises)

        return render_template("user.html", user=user, exercises=exercises, title="Dashboard")
    else:
        return redirect(url_for("login"))
    

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
        user_authentication, sql_id = search(username, password)
        print(username, password)
        if user_authentication:
            session["user_id"] = sql_id
            print("User authenticated in login function")
            return redirect(url_for("get_user_id", user_id=sql_id))
        else:
            error_message = "Invalid login credentials. Please try again. (Usernames and passwords are case sensitive, spaces also count as cahracters that must be re-entered)"
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
    with sqlite3.connect(database_file) as connection:
        cursor = connection.cursor()
        sql = "SELECT * FROM User WHERE name = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()
        if user and username == user[1]:
            error_message = "Username is taken, please use another name"
            return render_template("signup.html", title="Sign up", error_message=error_message)
        if password == confirm_password:
            cursor.execute("INSERT INTO User (name, password) VALUES (?, ?)", (username, password))
            connection.commit()
            return render_template("login.html", title="Log in")
        else:
            error_message = "Your confirmed password is incorrect, please try again"
            return render_template("signup.html", title="Sign up", error_message=error_message)


@app.route('/add_lift', methods=['GET', 'POST'])
def add_lift_route():
    if 'user_id' in session:
        user_id = session['user_id']

        if request.method == 'POST':
            lift_name = request.form.get('name')
            weight = request.form.get('weight')
            description = request.form.get('description')

            with sqlite3.connect(database_file) as connection:
                cursor = connection.cursor()

                sql = "INSERT INTO Exercise (name, description, weight, user_id) VALUES (?, ?, ?, ?)"
                cursor.execute(sql, (lift_name, description, weight, user_id))
                connection.commit()
            return redirect(url_for('get_user_id', user_id=user_id))

        return render_template('add_lift.html', title='Add Lift')
    else:
        return redirect(url_for('login'))


@app.route('/edit_lift/<int:lift_id>', methods=['GET', 'POST'])
def edit_lift_route(lift_id):
    if 'user_id' in session:
        user_id = session['user_id']

        if request.method == 'POST':
            new_weight = request.form.get('weight')

            with sqlite3.connect(database_file) as connection:
                cursor = connection.cursor()

                # Update the weight for the specified exercise
                sql = "UPDATE Exercise SET weight = ? WHERE id = ? AND user_id = ?"
                cursor.execute(sql, (new_weight, lift_id, user_id))
                connection.commit()
                return redirect(url_for('get_user_id', user_id=user_id))

        with sqlite3.connect(database_file) as connection:
            cursor = connection.cursor()

            # Retrieve the exercise details
            sql = "SELECT * FROM Exercise WHERE id = ? AND user_id = ?"
            cursor.execute(sql, (lift_id, user_id))
            exercise = cursor.fetchone()

        return render_template('edit_lift.html', title='Edit Lift', exercise=exercise)
    else:
        return redirect(url_for('login'))

@app.route('/delete_lift/<int:lift_id>', methods=['POST'])
def delete_lift_route(lift_id):
    if 'user_id' in session:
        user_id = session['user_id']

        with sqlite3.connect(database_file) as connection:
            cursor = connection.cursor()

            # Check if the exercise with the specified ID belongs to the current user
            sql_check = "SELECT id FROM Exercise WHERE id = ? AND user_id = ?"
            cursor.execute(sql_check, (lift_id, user_id))
            exercise = cursor.fetchone()

            if exercise:
                # If the exercise belongs to the user, delete it
                sql_delete = "DELETE FROM Exercise WHERE id = ?"
                cursor.execute(sql_delete, (lift_id,))
                connection.commit()

        return redirect(url_for('get_user_id', user_id=user_id))

    return redirect(url_for('login'))

# Custom error handling for page not found errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error='Page not found'), 404


# Custom error handling for 500 (Internal Server Error) error
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error='Internal server error'), 500


# Custom error handling for other unexpected errors
@app.errorhandler(Exception)
def unexpected_error(error):
    return render_template('error.html', error='Something went wrong'), 500

if __name__ == '__main__':
    app.run(debug=True)
