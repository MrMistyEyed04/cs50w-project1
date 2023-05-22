import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    tabla1=text("""CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL
    );   
    """)
    db.execute(tabla1)

    tabla2=text("""CREATE TABLE libro (
    id SERIAL PRIMARY KEY,
    ISBN TEXT NOT NULL,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    año_publication text NOT NULL
    );   
    """)
    db.execute(tabla2)

    tabla3=text("""CREATE TABLE reseñas (
    id SERIAL PRIMARY KEY,
    usuario NUMERIC NOT NULL,
    reseña TEXT NOT NULL,
    puntuaje NUMERIC NOT NULL
    );   
    """)
    db.execute(tabla3)

    db.commit()

if __name__ == "__main__":
    main()
