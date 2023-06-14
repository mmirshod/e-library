"""
Data Models for e-Library API
"""

import os

from flask_sqlalchemy import SQLAlchemy

DB_HOST = os.getenv("DB_HOST", "127.0.0.1:5432")
DB_USER = os.getenv("DB_USER", "mildof")
DB_PASSWORD = os.getenv("DB_PASSWORD", " ")
DB_NAME = os.getenv("DB_NAME", "test_lib")
DB_PATH = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


db = SQLAlchemy()


def setup_db(app, database_path=DB_PATH):
    """
    Gets Flask Application instance and database path. Initialize Database and bind application with SQLAlchemy service
    """

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

    with app.app_context():
        db.app = app
        db.init_app(app)


def db_drop_and_create_all() -> None:
    """
    Clean the database.
    Can be used to test application and initialize fresh app.
    """

    db.drop_all()
    db.create_all()


class Author(db.Model):
    __tablename__ = "author"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer, nullable=True)

    # Relationships:
    books = db.relationship("Book", lazy=True, backref="author")
    genres = db.relationship("Genre", secondary="author_genre", backref="authors")

    def __repr__(self):
        print(f"<Author '{self.name}', {self.age}>")

    def insert(self) -> None:
        """Add Author instance to database."""

        db.session.add(self)
        db.session.commit()

    def short(self) -> dict:
        """Short representation of Author instance."""

        return {
            "id": self.id,
            "name": self.name
        }

    def long(self) -> dict:
        """Long representation of Author instance."""

        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "books": [book.short() for book in self.books],
            "genres": [genre.format() for genre in self.genres]
        }

    def update(self) -> None:
        """Update Author instance in database"""
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def delete(self) -> None:
        """Delete Author instance from database."""
        try:
            db.session.delete(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship("Book", backref="category", lazy=True)

    def short(self) -> dict:
        return {
            "name": self.name,
            "num_of_books": len(self.books)
        }

    def long(self) -> dict:
        return {
            "name": self.name,
            "books": [book.short() for book in self.books],
            "num_of_books": len(self.books)
        }

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()


class Book(db.Model):
    """ Book entity, extends the base SQLAlchemy Model """

    __tablename__ = "book"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    rating = db.Column(db.Float, default=0.0)  # Average rating of the book
    rates = db.Column(db.Integer, default=0)  # How many people rated the book
    downloads = db.Column(db.Integer, default=0)  # How many times book was downloaded
    num_of_pages = db.Column(db.Integer, default=0)
    year_of_publishing = db.Column(db.Integer, default=1999)

    # Relationships:
    genres = db.relationship("Genre", secondary="book_genre", backref="books")
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"), nullable=False)

    def short(self) -> dict:
        return {
            "id": self.id,
            "author": self.author.name,
            "title": self.name,
            "rating": self.rating,
            "downloads": self.downloads,
        }

    def long(self) -> dict:
        return {
            "id": self.id,
            "title": self.name,
            "num_of_pages": self.num_pages,
            "year_of_publishing": self.year_of_publishing,
            "author": self.author.name,
            "category": self.category.name,
            "genres": [genre.format() for genre in self.genres],
            "description": self.description,
            "rating": round(self.rating, 1),
            "rates": self.rates,
            "downloads": self.downloads,
        }

    def insert(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update(self) -> None:
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()


class Genre(db.Model):
    __tablename__ = "genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

    def format(self) -> str:
        return self.name

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

    def update(self):
        try:
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()


author_genre = db.Table(
    "author_genre",
    db.Column("author_id", db.Integer, db.ForeignKey("author.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True)
)

book_genre = db.Table(
    "book_genre",
    db.Column("book_id", db.Integer, db.ForeignKey("book.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genre.id"), primary_key=True)
)
