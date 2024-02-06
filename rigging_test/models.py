from extensions import db
from datetime import date
from enum import Enum


class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_type_id = db.Column(db.Integer, db.ForeignKey('component_type.id'), nullable=False)

    #def __repr__(self):
    #    return f'<Manifacturer {self.manufacturer}>'

    serial_number = db.Column(db.String(50), nullable=False)
    dom = db.Column(db.Date, default=date.today, nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False)

    # La relación con Rig se maneja a través de la tabla de asociación en el modelo Rig
    # Eliminada la relación directa rig_id y la relación backref de Rig a Component
    #rigs = db.relationship('Rig', secondary=rig_component_association, back_populates="components")
    #riggings = db.relationship('Rigging', backref='associated_component', lazy='dynamic')

    # Opcional: Propiedades o métodos adicionales según sea necesario

    def __repr__(self):
        return f'<Component {self.serial_number}>'

class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Manufacturer {self.manufacturer}>'


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=False)

    # Relationship to link back to Component
    components = db.relationship('Component', backref='size', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Size {self.size}>'

class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False)

    # Relationship to link back to Component
    components = db.relationship('Component', backref='status', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Status {self.status}>'


class ComponentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_type = db.Column(db.String(50), nullable=False)

    # Relationship to link back to Component
    components = db.relationship('Component', backref='component_type', lazy=True, cascade="all, delete-orphan")
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
