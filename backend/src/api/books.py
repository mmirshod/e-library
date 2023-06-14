from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import exc
import os

from backend.src.database.models import Book, db, Author, Category, Genre
from backend.src.database.schemas import BookSchema
from backend.src.auth.auth import require_auth


blp = Blueprint("books", __name__, description="Operations on books")


@blp.route("/book")
class BookList(MethodView):
    @require_auth("get:books")
    def get(self):
        books = [book.short() for book in Book.query.all()]

        return jsonify({
            "success": True,
            "books": books
        }), 200

    @require_auth("post:books")
    @blp.arguments(BookSchema)
    def post(self, data):
        """
        Get new book's data in form of JSON data. e.g.:
        {
            "name": string | <title_of_the_book>,
            "author": string | <name_of_the_author>,
            "category": string | <name_of_category>,
            "num_of_pages": int | <number of pages in the book>,
            "year_of_publishing": int | <year of publishing of the book in the form: yyyy>,
            "genres": list<string> | <list with genre names>,
            "description": string | <description of the book>,
        }
        """
        try:
            author = Author.query.filter_by(name=data["author"]).one_or_none()
            category = Category.query.filter_by(name=data["category"]).one_or_none()
            file = request.files["book"]
            file.save(os.path.join("../../resources/books", data["name"]))

            book = Book(
                name=data["name"],
                description=data["description"],
                author=author.id,
                rating=0.0,
                rates=0,
                downloads=0,
                num_of_pages=data['num_of_pages'],
                year_of_publishing=data['year_of_publishing'],
                category_id=category.id
            )

            for genre_name in data["genres"]:
                genre = Genre.query.filter_by(name=genre_name)
                book.genres.append(genre)
        
            book.insert()

            return jsonify({
                "success": True,
                "new_book": book.short()
            }), 201
        except exc:
            print(exc)
            db.session.rollback()
        finally:
            db.session.close()


@blp.route("/books/<int:id>")
class Book(MethodView):
    @require_auth("get:books-details")
    def get(self, id: int):
        try:
            book = Book.query.filter_by(id=id)
            
            return jsonify({
                "success": True,
                "book": book.long()
            }), 200
        except:
            # user inputted book's id by himself
            abort(404, message="REQUESTED BOOK DOES NOT EXIST")

    @require_auth("delete:books")
    def delete(self, id: int):
        book = Book.query.filter_by(id=id)

        if not book:
            abort(404, message="BOOK NOT FOUND")

        try:
            book.delete()
            return jsonify({
                "success": True,
                "deleted_book_id": book.id
            }), 200
        except exc:
            print(exc)
            db.session.rollback()
        finally:
            db.session.close()

    # @require_auth("patch:books")
    def patch(self, id: int):
        """
        Get new book's data in form of JSON data. e.g.:
        {
            "id": int,
            "title": string | name of the book,
            "num_of_pages": int,
            "year_of_publishing": int | year like 1999,
            "author": string | only name of the author,
            "category": string | category name,
            "genres": list<string> | list with names of genres
            "description": string,
            "rating": float,
            "rates": int, number of rates,
            "downloads": int, number of downloads
        }
        """
        book = Book.query.filter_by(id=id)  # get book
        json_data = request.get_json()  # get json data

        if id != int(json_data["id"]):  # user changed or sent by himself json data to server
            abort(422)

        if not book:  # user typed URL by himself
            abort(404)

        if not json_data:  # server did not receive data to update
            abort(422)

        author = Author.query.filter_by(name=json_data["author"])

        if not author: # probably user sent json data by himself
            abort(422)

        category = Category.query.filter_by(name=json_data["category"])

        if not category:  # probably user sent json by himself
            abort(422)

        try:
            book.name = json_data["title"]
            book.num_pages = json_data["num_of_pages"]
            book.year_of_publishing = json_data["year_of_publishing"]
            book.author = author
            book.category = category
            book.description = json_data["description"]
            book.rating = json_data["rating"]
            book.rates = json_data["rates"]
            book.downloads = json_data["downloads"]

            for genre in json_data["genres"]:
                genre_object = Genre.query.filter_by(name=genre).one_or_none()
                
                if genre_object:
                    book.genres.append(genre_object)        
            book.update()
    
        except exc:
            print(exc)
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
 