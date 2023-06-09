import os
import requests

import csv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
engine = create_engine("postgresql://postgres:AwHB8WKoQmOrj3fWpmgy@containers-us-west-67.railway.app:6724/railway")

db = scoped_session(sessionmaker(bind=engine))

def main():
    libros = open("books.csv")
    leer = csv.reader(libros)
    i = 0
    cont = 0
    for isbn, title, author, year in leer:
        if (i == 0):
            i = 1
        else:
            insertar = text("INSERT INTO books (isbn, title, author, year) values(:isbn,:title,:author,:year)")
            db.execute(insertar, {"isbn":isbn,"title":title,"author":author,"year":year})
            db.commit()
            cont = cont + 1
        print(cont, end=" ")
        print(f"{isbn} - {title} - {author} - {year}")

main()