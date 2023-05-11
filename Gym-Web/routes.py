from flask import Flask, render_template
import sqlite3


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html", title = "Home Page")

@app.route("/Signup")
def signup():
    return render_template("signup.html",title = "Sign up")

if __name__ == '__main__':
    app.run(debug = True)