import csv
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def read_file(filename, col_list):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
 
        for row in reader:    
            dato1=text("INSERT INTO libro (isbn, titulo, autor, año_publication) VALUES (:isbn, :titulo, :author, :year)")
            db.execute(dato1,
                    {"isbn": row["isbn"], "titulo":row["title"], "author":row["author"], "year":row["year"]})
            db.commit()
                    

def main():
    read_file('books.csv', ['isbn', 'title', 'author', 'year'])
    
    


if __name__ == "__main__":
    main()