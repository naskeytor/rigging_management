from flask import Flask, render_template, request, redirect, url_for
from extensions import db, migrate
from models import Manufacturer, Size, Status, ComponentType

app = Flask(__name__)
app.config['SECRET_KEY'] = '3664atanas'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:3664atanas@localhost:3306/rigging'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def index():
    return render_template('index.html')


#####################       Manifacturer


@app.route('/manufacturers')
def view_manufacturers():
    manufacturers = Manufacturer.query.all()
    return render_template('view_manufacturers.html', manufacturers=manufacturers)

@app.route('/manufacturer/add', methods=['GET', 'POST'])
def add_manufacturer():
    message = None
    if request.method == 'POST':
        # Handle the form submission
        new_manufacturer = Manufacturer(manufacturer=request.form['manufacturer'])
        db.session.add(new_manufacturer)
        db.session.commit()
        message = "New manufacturer added successfully."
    return render_template('add_manufacturer.html', message=message)


#####################       Size


@app.route('/sizes')
def view_sizes():
    sizes = Size.query.all()
    return render_template('view_sizes.html', sizes=sizes)

@app.route('/size/add', methods=['GET', 'POST'])
def add_size():
    message = None
    if request.method == 'POST':
        new_size = Size(size=request.form['size'])
        db.session.add(new_size)
        db.session.commit()
        message = "New size added successfully."
    return render_template('add_size.html', message=message)


#####################       Status


@app.route('/statuses')
def view_statuses():
    statuses = Status.query.all()
    return render_template('view_statuses.html', statuses=statuses)

@app.route('/status/add', methods=['GET', 'POST'])
def add_status():
    message = None
    if request.method == 'POST':
        new_status = Status(status=request.form['status'])
        db.session.add(new_status)
        db.session.commit()
        message = "New status added successfully."
    return render_template('add_status.html', message=message)

####################        COmponent types


@app.route('/component_types')
def view_component_types():
    component_types = ComponentType.query.all()
    return render_template('view_component_types.html', component_types=component_types)

@app.route('/component_type/add', methods=['GET', 'POST'])
def add_component_type():
    message = None
    if request.method == 'POST':
        new_type = ComponentType(component_type=request.form['component_type'])
        db.session.add(new_type)
        db.session.commit()
        message = "New component type added successfully."
    return render_template('add_component_type.html', message=message)


if __name__ == '__main__':
    app.run(debug=True)
