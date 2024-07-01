from flask import Flask, render_template
from rigging_test.extensions import db, migrate
from flask_login import LoginManager
from rigging_test.models.models import User
from rigging_test.config import DevelopmentConfig
from rigging_test.context_processors import (inject_rigging_types, inject_rigs, inject_rigging_sizes, inject_manufacturers,
                                inject_rigging, inject_rigging_components, inject_component_processor)
import mysql.connector
from mysql.connector import errorcode

def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    # Create database if it doesn't exist
    db_name = app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[-1]
    db_uri = app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[0] + "/mysql"
    try:
        cnx = mysql.connector.connect(user='root', password='3664atanas', host='localhost')
        cursor = cnx.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    except Exception as e:
        print(f"An error occurred: {e}")

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirige a la vista de login si no está autenticado

    db.init_app(app)
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from rigging_test.blueprints.components.routes import components_bp
    from rigging_test.blueprints.rigs.routes import rigs_bp
    from rigging_test.blueprints.rigging.routes import rigging_bp
    from rigging_test.blueprints.manufacturers.routes import manufacturers_bp
    from rigging_test.blueprints.sizes.routes import sizes_bp
    from rigging_test.blueprints.statuses.routes import statuses_bp
    from rigging_test.blueprints.component_types.routes import component_types_bp
    from rigging_test.blueprints.models.routes import models_bp
    from rigging_test.blueprints.main.routes import main_bp
    from rigging_test.blueprints.auth.routes import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(components_bp)
    app.register_blueprint(rigs_bp)
    app.register_blueprint(rigging_bp)
    app.register_blueprint(manufacturers_bp)
    app.register_blueprint(sizes_bp)
    app.register_blueprint(statuses_bp)
    app.register_blueprint(component_types_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(main_bp)

    app.context_processor(inject_rigging)
    app.context_processor(inject_rigging_types)
    app.context_processor(inject_rigging_components)
    app.context_processor(inject_rigs)
    app.context_processor(inject_component_processor)
    app.context_processor(inject_rigging_sizes)
    app.context_processor(inject_manufacturers)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
