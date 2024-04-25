#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

# Instantiate REST API
api = Api(app)

@app.route('/')
def home():
    return '<h1>Code challenge</h1>'

class Vendors(Resource):
        def get(self):
            vendors = [vendor.to_dict(exclude=['vendor_sweets']) for vendor in Vendor.query.all()]
            return make_response(jsonify(vendors), 200)

api.add_resource(Vendors, '/vendors')

class VendorByID(Resource):
    def get(self, id):
        vendor = Vendor.query.filter_by(id=id).first()
        if vendor:
            return make_response(jsonify(vendor.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Vendor not found"}), 404)

api.add_resource(VendorByID, '/vendors/<int:id>')

class Sweets(Resource):
    def get(self):
        sweets = [sweet.to_dict() for sweet in Sweet.query.all()]
        return make_response(jsonify(sweets), 200)

api.add_resource(Sweets, '/sweets')

class SweetByID(Resource):
    def get(self, id):
        sweet = Sweet.query.filter_by(id=id).first()
        if sweet:
            return make_response(jsonify(sweet.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Sweet not found"}), 404)

api.add_resource(SweetByID, '/sweets/<int:id>')

class VendorSweets(Resource):
    def post(self):
        data = request.get_json()

        if 'price' not in data or 'vendor_id' not in data or 'sweet_id' not in data:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        price = data['price']
        vendor_id = data['vendor_id']
        sweet_id = data['sweet_id']

        # Check if the vendor and sweet exist
        vendor = Vendor.query.get(vendor_id)
        sweet = Sweet.query.get(sweet_id)

        if not vendor or not sweet:
            return make_response(jsonify({"errors": ["Vendor or sweet not found"]}), 404)

        # Validate price
        try:
            validated_price = VendorSweet().validate_price('price', price)
        except ValueError as e:
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        # Create new VendorSweet
        new_vendor_sweet = VendorSweet(price=validated_price, vendor_id=vendor_id, sweet_id=sweet_id)
        db.session.add(new_vendor_sweet)
        db.session.commit()

        return make_response(jsonify(new_vendor_sweet.to_dict()), 201)


api.add_resource(VendorSweets, '/vendor_sweets')

class VendorSweetByID(Resource):
    def delete(self, id):
        vendor_sweet = VendorSweet.query.get(id)
        if not vendor_sweet:
            return make_response(jsonify({"error": "VendorSweet not found"}), 404)

        db.session.delete(vendor_sweet)
        db.session.commit()

        return make_response(jsonify({}), 204)

api.add_resource(VendorSweetByID, '/vendor_sweets/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
