from flask import Flask
from flask_smorest import Api

from backend.src.api.authors import blp as AuthorBluePrint
from backend.src.api.books import blp as BookBluePrint
from backend.src.database.models import db_drop_and_create_all, setup_db

app = Flask(__name__)

app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "e-Library"
app.config["API_VERSION"] = "v0.1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"


api = Api(app)

api.register_blueprint(BookBluePrint)
api.register_blueprint(AuthorBluePrint)


with app.app_context():
    setup_db(app)
    db_drop_and_create_all()


###################################################################################
#                                'GET' ROUTES                                     #
###################################################################################

# @app.route("/categories/<int:category_id>", methods=["GET"])
# @require_auth("get:categories_details")
# def get_category_details(category_id: int):
#     try:
#         category = Category.query.filter_by(id=category_id)

#         return jsonify({
#             "success": True,
#             "category": category.long()
#         })
#     except:
#         abort(404)


# @app.route("/categories", methods=["POST"])
# @require_auth("post:categories")
# def post_category():
#     """
#     JSON data format:
#     {
#         "name": string | name of the category,
#         "books": list<string> | titles of the books related to this category
#     }
#     """

#     json_data = request.get_json()

#     if not json_data:
#         abort(422)

#     if set(json_data.keys()) != set("name", "books"):
#         abort(422)

#     try:
#         category = Category(name=json_data["name"])

#         for book_name in json_data["books"]:
#             book = Book.query.filter_by(name=book_name)
#             if book:
#                 category.books.append(book)

#         category.insert()

#     except exc:
#         print(exc)
#         db.session.rollback()
#     finally:
#         db.session.close()


# @app.route("/genres", methods=["POST"])
# @require_auth("post:genres")
# def post_genre():
#     """
#     Format of the JSON data:
#     {
#         "name": string | name of the genre,
#     }
#     """
#     json_data = request.get_json()

#     if not json_data:
#         abort(422)

#     if not json_data["name"]:
#         abort(422)
    
#     try:
#         genre = Genre(name=json_data["name"])
#         genre.insert()

#     except exc:
#         print(exc)
#         db.session.rollback()
#     finally:
#         db.session.close()


if __name__ == '__main__':
    app.run()
    