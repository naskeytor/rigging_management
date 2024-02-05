from flask import Flask, render_template, request, redirect, url_for
from extensions import db, migrate
from models import Manufacturer, Size, Status, ComponentType, Model

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

@app.route('/manufacturer/edit/<int:id>', methods=['GET', 'POST'])
def edit_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    if request.method == 'POST':
        manufacturer.manufacturer = request.form['manufacturer']
        db.session.commit()
        return redirect(url_for('view_manufacturers'))
    return render_template('edit_manufacturer.html', manufacturer=manufacturer)

@app.route('/manufacturer/delete/<int:id>', methods=['POST'])
def delete_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    db.session.delete(manufacturer)
    db.session.commit()
    return redirect(url_for('view_manufacturers'))


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

@app.route('/size/edit/<int:id>', methods=['GET', 'POST'])
def edit_size(id):
    size = Size.query.get_or_404(id)
    if request.method == 'POST':
        size.size = request.form['size']
        db.session.commit()
        return redirect(url_for('view_sizes'))
    return render_template('edit_size.html', size=size)

@app.route('/size/delete/<int:id>', methods=['POST'])
def delete_size(id):
    size = Size.query.get_or_404(id)
    db.session.delete(size)
    db.session.commit()
    return redirect(url_for('view_sizes'))


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

@app.route('/status/edit/<int:id>', methods=['GET', 'POST'])
def edit_status(id):
    status = Status.query.get_or_404(id)
    if request.method == 'POST':
        status.status = request.form['status']
        db.session.commit()
        return redirect(url_for('view_statuses'))
    return render_template('edit_status.html', status=status)

@app.route('/status/delete/<int:id>', methods=['POST'])
def delete_status(id):
    status = Status.query.get_or_404(id)
    db.session.delete(status)
    db.session.commit()
    return redirect(url_for('view_statuses'))

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

@app.route('/component_type/edit/<int:id>', methods=['GET', 'POST'])
def edit_component_type(id):
    component_type = ComponentType.query.get_or_404(id)
    if request.method == 'POST':
        component_type.component_type = request.form['component_type']
        db.session.commit()
        return redirect(url_for('view_component_types'))
    return render_template('edit_component_type.html', component_type=component_type)

@app.route('/component_type/delete/<int:id>', methods=['POST'])
def delete_component_type(id):
    component_type = ComponentType.query.get_or_404(id)
    db.session.delete(component_type)
    db.session.commit()
    return redirect(url_for('view_component_types'))

@app.route('/models')
def view_models():
    models = Model.query.all()
    return render_template('view_models.html', models=models)

@app.route('/model/add', methods=['GET', 'POST'])
def add_model():
    message = None
    if request.method == 'POST':
        new_model = Model(
            model=request.form['model'],
            manufacturer_id=request.form['manufacturer_id']
        )
        db.session.add(new_model)
        db.session.commit()
        message = "New model added successfully."

    manufacturers = Manufacturer.query.all()
    return render_template('add_model.html', manufacturers=manufacturers, message=message)

@app.route('/model/edit/<int:id>', methods=['GET', 'POST'])
def edit_model(id):
    model = Model.query.get_or_404(id)
    if request.method == 'POST':
        model.model = request.form['model']
        model.manufacturer_id = request.form['manufacturer_id']
        db.session.commit()
        return redirect(url_for('view_models'))

    manufacturers = Manufacturer.query.all()
    return render_template('edit_model.html', model=model, manufacturers=manufacturers)

@app.route('/model/delete/<int:id>', methods=['POST'])
def delete_model(id):
    model = Model.query.get_or_404(id)
    db.session.delete(model)
    db.session.commit()
    return redirect(url_for('view_models'))



if __name__ == '__main__':
    app.run(debug=True)
