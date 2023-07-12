import os
from flask import Flask, session, render_template, redirect, request, flash,jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import *
from cs50 import SQL
import requests


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
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    username = request.form.get("username")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="Debe escribir un nombre de usuario")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="Debe escribir una contraseña")

        sql_expression = text('SELECT * FROM users WHERE username = :username')
        rows = db.execute(sql_expression, {"username": username})
        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message="Nombre de usuario/contraseña invalida")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """
    
    # Forget any user_id
    session.clear()
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="Debe escribir un nombre de usuario")

        # Query database for username
        query = text("SELECT * FROM users WHERE username = :username")
        userCheck = db.execute(query, {"username": request.form.get("username")}).fetchone()


        # Check if username already exist
        if userCheck:
            return render_template("error.html", message="Nombre de usuario ya existente")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="Debe escribir una contraseña")

        # Ensure confirmation wass submitted 
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="Debe confirmar la contraseña")

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="Contraseñas distintas")
        
        # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        
        # Insert register into DB
        query = text("INSERT INTO users (username, password) VALUES (:username, :password)").bindparams(
        username=request.form.get("username"),
        password=hashedPassword)

        db.execute(query)

        # Commit changes to database
        db.commit()

        flash('Cuenta creada', 'info')

        # Redirect user to index page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/search", methods=["GET"])
@login_required
def search():
    """ Get books results """

    # Check book id was provided
    if not request.args.get("book"):
        return render_template("error.html", message="Debe proporcionar un libro.")

    # Take input and add a wildcard
    query = "%" + request.args.get("book") + "%"

    # Capitalize all words of input for search
    # https://docs.python.org/3.7/library/stdtypes.html?highlight=title#str.title
    query = query.title()
    
    sql_expression = text('SELECT isbn, title, author, year FROM books WHERE \
                       isbn LIKE :query OR \
                       title LIKE :query OR \
                       author LIKE :query LIMIT 15')

    rows = db.execute(sql_expression, {"query": query})
    
    # Books not founded
    if rows.rowcount == 0:
        return render_template("error.html", message="No se pudo encontrar ningun libro con esa descripcion.")
    
    # Fetch all the results
    books = rows.fetchall()

    return render_template("results.html", books=books)

@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):
    """ Save user review and load same page with reviews updated."""

    if request.method == "POST":

        # Save current user info
        currentUser = session["user_id"]
        
        # Fetch form data
        rating = request.form.get("rating")
        comment = request.form.get("comment")
        
        # Search book_id by ISBN
        query = text("SELECT id FROM books WHERE isbn = :isbn")
        row = db.execute(query, {"isbn": isbn})

        # Save id into variable
        bookId = row.fetchone() # (id,)
        bookId = bookId[0]

        # Check for user submission (ONLY 1 review/user allowed per book)
        query = text("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id")
        row2 = db.execute(query, {"user_id": currentUser, "book_id": bookId})

        # A review already exists
        if row2.rowcount == 1:
            
            flash('Ya has enviado una reseña para este libro.', 'warning')
            return redirect("/book/" + isbn)

        # Convert to save into DB
        rating = int(rating)

        query = text("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES (:user_id, :book_id, :comment, :rating)")
        db.execute(query, {"user_id": currentUser, "book_id": bookId, "comment": comment, "rating": rating})

        # Commit transactions to DB and close the connection
        db.commit()

        flash('Reseña enviada!', 'info')

        return redirect("/book/" + isbn)
    
    # Take the book ISBN and redirect to his page (GET)
    else:

        query = text("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn")
        row = db.execute(query, {"isbn": isbn})

        bookInfo = row.fetchall()

        """ GOODREADS reviews """

        # Read API key from env variable
        key = os.getenv("GOODREADS_KEY")
        
        # Query the api with key and ISBN as parameters
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})

        # Convert the response to JSON
        response = query.json()

        # "Clean" the JSON before passing it to the bookInfo list
        response = response['books'][0]

        # Append it as the second element on the list. [1]
        bookInfo.append(response)

        """ Users reviews """

         # Search book_id by ISBN
        query = text("SELECT id FROM books WHERE isbn = :isbn")
        row = db.execute(query, {"isbn": isbn})

        # Save id into variable
        book = row.fetchone() # (id,)
        book = book[0]

        # Fetch book reviews
        # Date formatting (https://www.postgresql.org/docs/9.1/functions-formatting.html)
        query = text("""
    SELECT users.username, comment, rating,
    to_char(time, 'DD Mon YY - HH24:MI:SS') as time
    FROM users
    INNER JOIN reviews
    ON users.id = reviews.user_id
    WHERE book_id = :book
    ORDER BY time
""")

        results = db.execute(query, {"book": book})

        reviews = results.fetchall()

        return render_template("book.html", bookInfo=bookInfo, reviews=reviews)

@app.route("/api/<isbn>", methods=['GET'])
@login_required
def api_call(isbn):

    # COUNT returns rowcount
    # SUM returns sum selected cells' values
    # INNER JOIN associates books with reviews tables

    row = db.execute("SELECT title, author, year, isbn, \
                    COUNT(reviews.id) as review_count, \
                    AVG(reviews.rating) as average_score \
                    FROM books \
                    INNER JOIN reviews \
                    ON books.id = reviews.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn})

    # Error checking
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 422

    # Fetch result from RowProxy    
    tmp = row.fetchone()

    # Convert to dict
    result = dict(tmp.items())

    # Round Avg Score to 2 decimal. This returns a string which does not meet the requirement.
    # https://floating-point-gui.de/languages/python/
    result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)  