from flask import jsonify
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy import exc

from backend.src.database.models import Book, Category, db
from backend.src.database.schemas import CategorySchema
from backend.src.auth.auth import require_auth


blp = Blueprint("categories", __name__, description="Operation with categories")


@blp.route("/categories")
class CategoryList(MethodView):
    @require_auth("get:categories")
    def get(self):
        categories = Category.query.all()
        data = [category.short() for category in categories]

        return jsonify({
            "success": True,
            "categories": data,
            "total": len(data)
        })

    @require_auth("post:categories")
    @blp.arguments(CategorySchema)
    def post(self, data):
        """
        JSON data format:
        {
             "name": string | name of the category,
             "books": list<string> | titles of the books related to this category
        }
        example:
        {
            "name": "Magic",
            "books": ["Harry Potter", "Alice's Adventures in the Wonderland", "Divergent"]
        }
        """
        try:
            new_category = Category()
            new_category.name = data["name"]

            new_category.books = []
            for book in data["books"]:
                book_obj = Book.query.filter_by(name=book)

                if book_obj:
                    new_category.books.append(book_obj)
                else:
                    abort(400, "BOOK NOT FOUND")

            new_category.insert()
        except exc:
            print(exc)
            db.session.rollback()
            abort(400)
        finally:
            db.session.close()


@blp.route("/categories/<int:id>")
class Category(MethodView):
    @require_auth("get:categories_details")
    def get(self, id: int):
        pass

    @require_auth("patch:categories")
    def patch(self, id: int):
        pass

    @require_auth("delete:categories")
    def delete(self, id: int):
        pass
