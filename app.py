from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app= Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "app.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String, unique=True) # nullable=False ?
    description = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)


    def __init__(self, name, image, description, price):
        self.name = name
        self.image = image
        self.description = description
        self.price = price


class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'image', 'description', 'price')

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/products/images', methods=['GET'])
def get_image_urls():
    products = db.session.query(Product).with_entities(Product.image, Product.name)
    response = [{"image": row[0],"name": row[1]} for row in products]
    # image = [product.image + product.name for product in products]
    # name = [product.name for product in products]
    return jsonify(response)

# ** ADD PRODUCT ENDPOINT **
@app.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    name = data.get("name")
    image = data.get("imageUrl")
    description = data.get("description")
    price = data.get("price")
    if not all([name, image, description, price]):
        return jsonify(error="Missing required fields"), 400
    if not isinstance(price, (int, float)):
        return jsonify(error="Price must be a number"), 400
    try:
        product = Product(name, image, description, price)
        db.session.add(product)
        db.session.commit()
        return jsonify(message="Product added successfully"), 201
    except Exception as e:
        return jsonify(error=str(e)), 500

# ** QUERY ALL ENDPOINT **
@app.route("/products", methods=["GET"])
def get_all_products():
    items = db.session.query(Product).all()
    return jsonify(products_schema.dump(items))

# ** UPDATE ENDPOINT **
@app.route("/products/<id>", methods=["PUT"])
def update_product(id):
    # data = request.get_json()
    product = Product.query.get(id)
    new_name = request.json.get("name")
    new_description = request.json.get("description")
    new_image = request.json.get("imageUrl")
    new_price = request.json.get("price")
    try:
        product.name = new_name
        product.description = new_description
        product.image = new_image
        product.price = new_price
        db.session.commit()
        return jsonify(message="Product updated successfully"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

# ** DELETE ENDPOINT **
@app.route("/products/<id>", methods=["DELETE"])
def delete_product(id):
    try:    
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify(message="Product deleted successfully"), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)