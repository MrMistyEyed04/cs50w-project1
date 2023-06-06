import os

from flask import Flask, session, render_template, redirect, request, flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

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

@app.route("/login", methods = ['GET', 'POST'])
def login ():
    if request.method == "POST":
        if not request.form.get("username"): # Si no recibo ningún dato desde el campo username de mi html, entonces retorna una plantilla html y manda un mensaje de error
            return render_template("login.html", message="Llena el campo username") # El message es la manipulación que yo haré para trabajar los distintos errores dentro de error.html
        if not request.form.get("password"): # Si no recibo ningún dato desde el campo password de mi html, entonces retorda una plantilla html y manda un mensaje de error
            return render_template("login.html", message="Llena el campo password")

        entrada = db.execute ("SELECT * FROM users WHERE username = :username",
                               username=request.form.get("username"))

        if len(entrada) != 1 or not check_password_hash(entrada[0]["password"], request.form.get("password")):
            return render_template("login.html", message="Nombre de usuario o contraseña incorrecto")

        session["user_id"]=entrada[0]["id_user"]
        session["username"]=entrada[0]["username"]
        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        #print(username)
        password = request.form.get("password")
        #print(password)
        
        if not username or not password:
            flash("Campos vacios")
            return render_template('register.html')
        
        seleccion = text("SELECT * FROM users WHERE name = :username")
        #print(seleccion)
        consulta = db.execute(seleccion, {"username" : username}).fetchone()
        print(consulta)
        if consulta != None:
            flash("Usuario ya existente")
            return render_template('register.html')
        hash = generate_password_hash(password)
        #print(hash)from PIL import Image
        insertar = text("INSERT INTO users (name, password) values(:username,:hash)")
        #print(insertar)
        db.execute(insertar, {"username" : username, "hash" : hash})
        db.commit()
        id = text("SELECT id FROM users WHERE name = :username")
        variable01 = db.execute(id,{"username":username}).fetchone()[0]
        db.commit()
        #print("Iniciando")
        #print(variable01)
        #print("Finalizando")
        session["logged_in"] = True
        posicion = int(variable01)
        session["users_id"] = posicion
        return redirect("/inicio")
    return render_template('register.html')



