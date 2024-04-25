from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Sweet(db.Model, SerializerMixin):
    __tablename__ = 'sweets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship

    vendor_sweets = db.relationship('VendorSweet', back_populates='sweet', cascade='all, delete-orphan')
    
    # Add association
    vendors = association_proxy('vendor_sweets', 'vendors',
                                 creator=lambda vendor_obj: VendorSweet(vendor=vendor_obj))
    
    def to_dict(self):
        data = {
            "id": self.id,
            "name": self.name,
        }
        return data
    
    # Add serialization

    serialize_rules = ('-vendor_sweets.sweet',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    
    def __repr__(self):
        return f'<Sweet {self.id}>'


class Vendor(db.Model, SerializerMixin):
    __tablename__ = 'vendors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    # Add relationship
    vendor_sweets = db.relationship('VendorSweet', back_populates='vendor', cascade='all, delete-orphan')
    
    # Add serialization
    serialize_rules = ('-vendor_sweets.vendor',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    # Add association
    sweets = association_proxy('vendor_sweets', 'sweet',
                                 creator=lambda sweet_obj: VendorSweet(sweet=sweet_obj))
    
    def to_dict(self, exclude=None):
        data = {
            "id": self.id,
            "name": self.name,
            "vendor_sweets": [sweet.to_dict() for sweet in self.sweets]  # Convert sweets to serializable format
        }
        if exclude:
            for field in exclude:
                data.pop(field, None)
        return data


    def __repr__(self):
        return f'<Vendor {self.id}>'


class VendorSweet(db.Model, SerializerMixin):
    __tablename__ = 'vendor_sweets'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Add relationships
    sweet = db.relationship('Sweet', back_populates='vendor_sweets')
    vendor = db.relationship('Vendor', back_populates='vendor_sweets')
    
    # Add serialization
    serialize_rules = ('-sweet.vendor_sweets','-vendor.vendor_sweets',)

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    sweet_id = db.Column(db.Integer, db.ForeignKey('sweets.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    
    # Add validation
    @validates('price')
    def validate_price(self, key, price):
        if price is None:
            raise ValueError('Price is required')
        if price < 0:
            raise ValueError('Price must be a positive number')
        return price
    
    def __repr__(self):
        return f'<VendorSweet {self.id}>'
