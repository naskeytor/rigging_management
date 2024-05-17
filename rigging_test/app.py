from flask import Flask, render_template
from extensions import db, migrate
from flask_login import LoginManager
from models.models import User, Role, Manufacturer, Size, Status, ComponentType, Model, Component, Rig, Rigging, RiggingType
from config import DevelopmentConfig
from context_processors import inject_rigging_types, inject_rigs, inject_rigging, inject_rigging_components, inject_component_processor

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    login_manager = LoginManager()
    login_manager.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from blueprints.auth.routes import auth_bp
    from blueprints.components.routes import components_bp
    from blueprints.rigs.routes import rigs_bp
    from blueprints.rigging.routes import rigging_bp
    from blueprints.manufacturers.routes import manufacturers_bp
    from blueprints.sizes.routes import sizes_bp
    from blueprints.statuses.routes import statuses_bp
    from blueprints.component_types.routes import component_types_bp
    from blueprints.models.routes import models_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(components_bp)
    app.register_blueprint(rigs_bp)
    app.register_blueprint(rigging_bp)
    app.register_blueprint(manufacturers_bp)
    app.register_blueprint(sizes_bp)
    app.register_blueprint(statuses_bp)
    app.register_blueprint(component_types_bp)
    app.register_blueprint(models_bp)

    app.context_processor(inject_rigging)
    app.context_processor(inject_rigging_types)
    app.context_processor(inject_rigging_components)
    app.context_processor(inject_rigs)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
