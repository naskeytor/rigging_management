from extensions import db
from datetime import date
from enum import Enum


class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Manufacturer {self.manufacturer}>'


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)

    # Relationship to link back to Component
    #components = db.relationship('Component', backref='size', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Size {self.size}>'

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)

    # Relationship to link back to Component
    #components = db.relationship('Component', backref='status', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Status {self.status}>'


class ComponentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_type = db.Column(db.String(50), nullable=False)

    # Relationship to link back to Component
    #components = db.relationship('Component', backref='component_type', lazy=True, cascade="all, delete-orphan")
    def __repr__(self):
        return f'<ComponentType {self.component_type}>'

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(50), nullable=False)
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)

    # Relationship with Manifacturer
    manufacturer = db.relationship('Manufacturer',
                                   backref=db.backref('models', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f'<Model {self.model}>'
