from marshmallow import Schema, fields


class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    author = fields.Str(required=True)
    category = fields.Str(required=True)
    description = fields.Str(required=True)
    num_of_pages = fields.Int(required=True)
    year_of_publishing = fields.Int(required=True)
    genres = fields.List(fields.Str(), required=True)

    # Optional Fields
    rating = fields.Float()
    rates = fields.Int()
    downloads = fields.Int()


class AuthorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Int(required=True)
    books = fields.List(fields.Str(), required=True)
    genres = fields.List(fields.Str(), required=True)


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    books = fields.List(fields.Str(), required=True)


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)



