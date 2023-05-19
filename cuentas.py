import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    creacion = text("""CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL
    );
    """)
    query=db.execute(creacion)
    creacion02 = text("""CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn TEXT,
    title TEXT,
    author TEXT,
    year TEXT
    );
    """)
    query02=db.execute(creacion02)
    creacion03 = text("""CREATE TABLE reviews (
    id_resena SERIAL NOT NULL,
    id_usuario INTEGER NOT NULL,
    id_libro INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT
    );
    """)
    query03=db.execute(creacion03)
    db.commit()

if __name__ == "__main__":
    main()