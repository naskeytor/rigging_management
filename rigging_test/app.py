from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, migrate
from models import Manufacturer, Size, Status, ComponentType, Model, Component, Rig, User
from utilities import find_component_by_serial, prepare_component_data
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '3664atanas'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:3664atanas@localhost:3306/rigging'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)
migrate.init_app(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # Redirige o maneja el flujo post-registro
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')



@app.route('/')
def index():
    return render_template('index.html')


#####################       Component

@app.route('/components')
def view_components():
    components = Component.query.all()
    return render_template('view_components.html', components=components)

@app.route('/component/add', methods=['GET', 'POST'])
def add_component():
    message = None
    if request.method == 'POST':
        # Extract data from form
        new_component = Component(
            component_type_id=request.form['component_type_id'],
            serial_number=request.form['serial_number'],
            dom=request.form.get('dom', None),
            size_id=request.form.get('size_id', None),
            status_id=request.form.get('status_id', None),
            model_id=request.form.get('model_id', None)
        )

        rig_id = request.form.get('rig_id')
        if rig_id:
            rig = Rig.query.get(rig_id)
            if rig:
                #new_component.rigs.append(rig)  # Asumiendo una relación de muchos a muchos
                new_component.rig_id = rig.id

        db.session.add(new_component)
        db.session.commit()
        message = "New component added successfully."
    component_types = ComponentType.query.all()
    component_sizes = Size.query.all()
    component_statuses = Status.query.all()
    component_models = Model.query.all()
    return render_template('add_component.html',
                            component_types=component_types,
                            component_sizes=component_sizes,
                            component_statuses=component_statuses,
                            component_models=component_models,
                            message=message)

@app.route('/component/edit/<int:id>', methods=['GET', 'POST'])
def edit_component(id):
    component = Component.query.get_or_404(id)
    component_types = ComponentType.query.all()  # Fetch all component types
    component_sizes = Size.query.all()  # Fetch all sizes
    component_statuses = Status.query.all()  # Fetch all statuses
    component_models = Model.query.all()
    #rigs = Rig.query.all()  # Fetch all rigs

    if request.method == 'POST':
        # Update component with form data
        component.component_type_id = request.form['component_type_id']
        component.serial_number = request.form['serial_number']
        component.dom = request.form.get('dom', None)
        component.size_id = request.form.get('size_id', None)
        component.status_id = request.form.get('status_id', None)
        component.model_id = request.form.get('model_id', None)

        db.session.commit()
        return redirect(url_for('view_components'))

    return render_template('edit_component.html',
                           component=component,
                           component_types=component_types,
                           component_sizes=component_sizes,
                           component_statuses=component_statuses,
                           component_models=component_models)

@app.route('/component/delete/<int:id>', methods=['POST'])
def delete_component(id):
    component = Component.query.get_or_404(id)
    db.session.delete(component)
    db.session.commit()
    return redirect(url_for('view_components'))


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

############################      RIGS

@app.route('/rigs')
def list_rigs():
    rigs = Rig.query.all()
    return render_template('rigs.html', rigs=rigs)

"""@app.route('/rigs/view/<int:rig_id>')
def view_rigs(rig_id):
    rigs = Rig.query.get_or_404(rig_id)
    return render_template('rigs.html', rig=rigs)"""


@app.route('/rigs/add', methods=['GET', 'POST'])
def add_rig():
    if request.method == 'POST':
        rig_number = request.form.get('rig_number')

        # Verifica si el número de rig ya existe
        existing_rig = Rig.query.filter_by(rig_number=rig_number).first()
        if existing_rig:
            error_message = "El número de rig ya existe. Por favor, elige otro."
            # Renderiza nuevamente el formulario con el mensaje de error y los datos necesarios para el formulario
            return render_template('add_rig.html', error_message=error_message)

        new_rig = Rig(rig_number=rig_number)

        db.session.add(new_rig)
        db.session.flush()

        # Asume que tienes funciones o métodos para encontrar el componente por serial y tipo
        # Por ejemplo: find_component_by_serial(serial_number, component_type)
        canopy_serial = request.form.get('canopy')
        container_serial = request.form.get('container')
        reserve_serial = request.form.get('reserve')
        aad_serial = request.form.get('aad')



        for serial, type_name in [(canopy_serial, 'Canopy'), (container_serial, 'Container'),
                                  (reserve_serial, 'Reserve'), (aad_serial, 'AAD')]:
            component = find_component_by_serial(serial, type_name)
            if component:
                new_rig.components.append(component)
                component.rig_id = new_rig.id  # Asegúrate de actualizar rig_id aquí


        db.session.commit()

        return redirect(url_for('list_rigs'))
    else:
        # Preparación de los datos necesarios para el formulario
        available_canopies, available_containers, available_reserves, available_aads = prepare_component_data()
        return render_template('add_rig.html', available_canopies=available_canopies,
                               available_containers=available_containers, available_reserves=available_reserves,
                               available_aads=available_aads)

@app.route('/rigs/delete/<int:rig_id>', methods=['POST'])
def delete_rig(rig_id):
    rig = Rig.query.get_or_404(rig_id)

    # Desasociar los componentes directos
    if hasattr(rig, 'direct_components'):
        for component in rig.direct_components:
            print(f"Desasociando rig_id para el componente: {component.serial_number}")
            component.rig_id = None
            db.session.add(component)  # Marcar el componente para la actualización

    # Desasociar los componentes en la tabla de asociación
    rig.components.clear()  # Esto desasocia todos los componentes relacionados en la tabla de asociación

    db.session.delete(rig)  # Eliminar el rig
    db.session.commit()  # Aplicar los cambios
    return redirect(url_for('list_rigs'))

@app.route('/rigs/edit/<int:rig_id>', methods=['GET', 'POST'])
def edit_rig(rig_id):
    rig = Rig.query.get_or_404(rig_id)
    if request.method == 'POST':
        rig_number = request.form.get('rig_number')
        existing_rig = Rig.query.filter_by(rig_number=rig_number).first()
        if existing_rig and existing_rig.id != rig.id:
            print("El número de rig ya existe. Por favor, elige otro.")
            return render_template('edit_rig.html', rig=rig)

        rig.rig_number = rig_number

        # Actualizar los componentes
        component_updates = {
            'Canopy': request.form.get('canopy'),
            'Container': request.form.get('container'),
            'Reserve': request.form.get('reserve'),
            'Aad': request.form.get('aad')
        }

        for type_name, serial in component_updates.items():
            if not serial:  # Si no se proporciona serial, continúa con el siguiente
                continue

            # Encuentra el componente actual de ese tipo (si existe)
            current_component = next((c for c in rig.components if c.component_type.component_type == type_name), None)

            # Si el componente actual tiene un serial diferente al proporcionado, actualiza la asociación
            if not current_component or current_component.serial_number != serial:
                # Desasociar el componente actual si es diferente
                if current_component:
                    rig.components.remove(current_component)
                    current_component.rig_id = None  # Actualizar rig_id en Component
                    db.session.add(current_component)

                # Asociar el nuevo componente
                new_component = Component.query.filter_by(serial_number=serial).first()
                if new_component:
                    rig.components.append(new_component)
                    new_component.rig_id = rig.id  # Actualizar rig_id en Component
                    db.session.add(new_component)
                else:
                    print(f"No se encontró el componente con serial {serial}.")

        db.session.commit()
        print("Rig actualizado con éxito")
        return redirect(url_for('list_rigs'))
    else:
        available_canopies, available_containers, available_reserves, available_aads = prepare_component_data()
        return render_template('edit_rig.html', available_canopies=available_canopies,
                               available_containers=available_containers, available_reserves=available_reserves,
                               available_aads=available_aads, rig=rig)



if __name__ == '__main__':
    app.run(debug=True)
