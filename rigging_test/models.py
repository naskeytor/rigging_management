from extensions import db
from datetime import date
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# Tabla de asociación
rig_component_association = db.Table('rig_component_association',
    db.Column('rig_id', db.Integer, db.ForeignKey('rig.id'), primary_key=True),
    db.Column('component_id', db.Integer, db.ForeignKey('component.id'), primary_key=True)
)

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    component_type_id = db.Column(db.Integer, db.ForeignKey('component_type.id'), nullable=False)

    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=True)  # Nueva clave foránea
    model = db.relationship('Model', backref='components')

    serial_number = db.Column(db.String(50), nullable=False)
    dom = db.Column(db.Date, default=date.today, nullable=False)
    size_id = db.Column(db.Integer, db.ForeignKey('size.id'), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=True)

    # La relación con Rig se maneja a través de la tabla de asociación en el modelo Rig
    # Eliminada la relación directa rig_id y la relación backref de Rig a Component
    rigs = db.relationship('Rig', secondary=rig_component_association, back_populates="components")

    rig = db.relationship('Rig', backref=db.backref('direct_components', lazy='dynamic', cascade="all, delete-orphan"))
    rig_id = db.Column(db.Integer, db.ForeignKey('rig.id'), nullable=True)  # Optional direct association

    def __repr__(self):
        return f'<Component {self.serial_number}>'

class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manufacturer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Manufacturer {self.manufacturer}>'


class Size(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    size = db.Column(db.String(50), nullable=True)

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




class Rig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rig_number = db.Column(db.String(10), nullable=False)
    components = db.relationship('Component', secondary=rig_component_association, back_populates="rigs")

    @property
    def canopy(self):
        for component in self.components:
            if component.component_type.component_type == 'Canopy':
                print(f"Canopy encontrado: {component.serial_number}")
                return component
        print("No se encontró un canopy.")
        return None

    @property
    def container(self):
        for component in self.components:
            if component.component_type.component_type == 'Container':
                return component
        return None

    @property
    def reserve(self):
        for component in self.components:
            if component.component_type.component_type == 'Reserve':
                return component
        return None

    @property
    def aad(self):
        for component in self.components:
            if component.component_type.component_type == 'Aad':
                return component
        return None

    # Relaciones con otros modelos como antes
    #riggings = db.relationship('Rigging', back_populates='rig')

    def __repr__(self):
        return f'<Rig {self.rig_number}>'
