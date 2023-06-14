from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import exc
from backend.src.database.models import Author, db, Book, Genre
from backend.src.auth.auth import require_auth
from backend.src.database.schemas import AuthorSchema


blp = Blueprint("authors", __name__, description="Operations on Author")


@blp.route("/authors")
class AuthorList(MethodView):

    @require_auth("get:authors")
    def get(self):
        authors = [author.short() for author in Author.query.all()]

        return jsonify({
            "success": True,
            "authors": authors
        }), 200

    @require_auth("post:authors")
    @blp.arguments(AuthorSchema)
    def post(self, data):
        """
        Example of JSON data:
        {
            "name": string | name of the author,
            "age": int | age of the author,
            "books": list<string> | name of the books,
            "genres": list<string> | name of the genres
        }
        """
        try:
            author = Author(
                name=data["name"],
                age=int(data["age"]),
            )

            for book_name in data["books"]:
                book = Book.query.filter_by(name=book_name).first()
                if book:
                    author.books.append(book)
                
            author.insert()

            return jsonify({
                "success": True,
                "new_author": author.short()
            }), 201
        except exc:
            print(exc)
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()


@blp.route("/authors/<int:id>")
class Author(MethodView):

    @require_auth("get:authors_details")
    def get(self, id: int):
        try:
            return jsonify({
                "success": True,
                "author": Author.query.filter_by(id=id).long()
            }), 200
        except exc:
            # user inputted author id by himself
            print(exc)
            abort(404, message="AUTHOR NOT FOUND")
    
    @require_auth("patch:authors")
    def patch(self, id: int):
        """Example JSON:
        {
            "id": int,
            "name": string,
            "age": int,
            "books": list<book> | list with short representation of books
            "genres": list<string> | list with names of genres
        }

        Example of short representation of book:
        {
            "id": int,
            "author": string | name of the author,
            "title": string | name of the book,
            "rating": float,
            "downloads": int | number of downloads
        }
        json_data["books"] = [
            {
                "id": 4,
                "author": "Rowling",
                "title": "Harry Potter 4",
                "rating": 4.6,
                "downloads": 12441
            },
            {
                "id": 2,
                "author": "Rowling",
                "title": "Harry Potter 2",
                "rating": 4.6,
                "downloads": 12441
            },
            {
                "id": 7,
                "author": "Rowling",
                "title": "Harry Potter 7",
                "rating": 4.6,
                "downloads": 12441
            },
        ]
        """
        
        author = Author.query.filter_by(id=id).one_or_none()

        if not author:
            abort(404)

        json_data = request.get_json()

        if not json_data:
            abort(422)

        if json_data["id"] != id:
            abort(422)
        
        try:
            author.name = json_data["name"]
            author.age = json_data["age"]

            for genre in json_data["genres"]:
                genre_object = Genre.query.filter_by(name=genre)

                if genre_object:
                    author.genres.append(genre_object)

            # check for removed books
            for book in author.books:
                found = False
                for json_book in json_data["books"]:
                    if book.id == json_book["id"]:
                        found = True
                        break
                if not found:
                    author.books.remove(book)

            # check for new books
            for book in json_data["books"]:
                book_object = Book.query.filter_by(id=book["id"])

                if book_object not in author.books:
                    author.books.append(book_object)

            return jsonify({
                "success": True,
                "updated_book": author.short()
            })
        except exc:
            print(exc)
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()

    @require_auth("delete:authors")
    def delete(self, id: int):
        author = Author.query.filter_by(id=id)

        if not author:
            abort(404, message="AUTHOR NOT FOUND")
        
        try:
            author.delete()
            return jsonify({
                "success": True,
                "deleted_author_id": author.id
            }), 200
        except exc:
            print(exc)
            db.session.rollback()
            abort(500)
        finally:
            db.session.close()
