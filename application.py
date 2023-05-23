import os

from flask import Flask, session, render_template, redirect, request, flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/Log_in", methods = ['GET', 'POST'])
def Log_in ():
    if request.method == "POST":
        #codigo inicio sesion
        return "xd"
    return render_template ('login.html')

@app.route("/Sign_up", methods = ['GET', 'POST'])
def Sign_up ():
    if request.method == "POST":
        #codigo inicio sesion
        return "xd"
    return render_template ('signup.html')



