from flask import Flask, render_template, request, redirect, url_for, flash
from extensions import db, migrate
from models import Manufacturer, Size, Status, ComponentType, Model, Component, Rig, User, Role, Rigging, RiggingType
from utilities import find_component_by_serial, prepare_component_data
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

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

        role = Role.query.filter_by(name='user').first()
        if not role:
            # Crear el rol si no existe
            role = Role(name='user')
            db.session.add(role)
            db.session.commit()

        user.roles.append(role)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        return redirect(url_for('index'))  # Redirige a los usuarios no administradores
    return render_template('admin_dashboard.html')


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.has_role('admin'):
        flash('Solo los administradores pueden editar usuarios.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        # Realiza aquí cualquier otra actualización necesaria
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('user_list'))

    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.has_role('admin'):
        flash('Solo los administradores pueden eliminar usuarios.', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('user_list'))


@app.route('/user_list')
@login_required
def user_list():
    if not current_user.is_admin():
        return redirect(url_for('index'))  # Solo permitir acceso a los administradores

    users = User.query.all()  # Obtener todos los usuarios
    return render_template('user_list.html', users=users)


@app.route('/create_role', methods=['GET', 'POST'])
@login_required
def create_role():
    if not current_user.is_admin():
        return redirect(url_for('index'))  # Asegúrate de que solo los admins puedan acceder

    if request.method == 'POST':
        role_name = request.form['role_name']
        if role_name:
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                new_role = Role(name=role_name)
                db.session.add(new_role)
                db.session.commit()
                flash('Rol creado exitosamente.', 'success')
            else:
                flash('El rol ya existe.', 'warning')
        else:
            flash('El nombre del rol no puede estar vacío.', 'danger')

        return redirect(url_for('list_roles'))

    # Si el método es GET, simplemente muestra el formulario
    return render_template('create_role_form.html')


@app.route('/list_roles')
@login_required
def list_roles():
    if not current_user.is_admin():
        return redirect(url_for('index'))  # Asegurarse de que solo los admins pueden ver los roles
    roles = Role.query.all()
    return render_template('role_list.html', roles=roles)


@app.route('/assign_roles', methods=['GET', 'POST'])
@app.route('/assign_roles/<int:user_id>', methods=['GET', 'POST'])
@login_required
def assign_roles(user_id=None):
    # Comprobar si el usuario actual es administrador.
    if not current_user.has_role('admin'):
        flash('Solo los administradores pueden asignar roles.', 'danger')
        return redirect(url_for('index'))

    users = User.query.all()
    roles = Role.query.all()
    selected_user = User.query.get(user_id) if user_id else None

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        selected_role_ids = request.form.getlist('role_ids')
        user = User.query.get(user_id)

        # Actualizar los roles del usuario
        user.roles = []
        for role_id in selected_role_ids:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        db.session.commit()
        flash('Roles asignados correctamente.', 'success')
        return redirect(url_for('user_list'))

    users = User.query.all()
    roles = Role.query.all()
    selected_user = User.query.get(user_id) if user_id else None
    return render_template('assign_roles.html', users=users, roles=roles, selected_user=selected_user)

@app.route('/delete_role/<int:role_id>', methods=['POST'])
@login_required
def delete_role(role_id):
    if not current_user.has_role('admin'):
        flash('Solo los administradores pueden eliminar roles.', 'danger')
        return redirect(url_for('index'))

    role = Role.query.get_or_404(role_id)

    # Eliminar el rol de todos los usuarios que lo tengan asignado
    for user in User.query.all():
        if role in user.roles:
            user.roles.remove(role)

    db.session.delete(role)
    db.session.commit()
    flash('Rol eliminado correctamente y desasignado de todos los usuarios.', 'success')
    return redirect(url_for('list_roles'))




@app.route('/')
def index():
    return render_template('index.html')


#####################       Component

@app.route('/components')
@app.route('/components/<component_type>')
def view_components(component_type=None):
    #component = Component.query.get_or_404(id)
    component_types = ComponentType.query.all()  # Fetch all component types
    component_sizes = Size.query.all()  # Fetch all sizes
    component_statuses = Status.query.all()  # Fetch all statuses
    component_models = Model.query.all()
    type_rigging = RiggingType.query.all()

    is_aad = False  # Inicializa la variable is_aad
    if component_type:
        component_type = component_type.capitalize()
        components = Component.query.join(ComponentType).filter(ComponentType.component_type == component_type).all()
        title = f"{component_type}"
        if component_type == "Aad":  # Comprueba si el tipo actual es AAD
            is_aad = True
    else:
        components = Component.query.all()
        title = "Todos los Componentes"

    return render_template('view_components.html', components=components, title=title, is_aad=is_aad,
                           component_types=component_types, component_sizes=component_sizes,
                           component_statuses=component_statuses, component_models=component_models,
                           type_rigging=type_rigging)


@app.route('/component/show/<int:component_id>')
@login_required
def show_component(component_id):
    component = Component.query.get_or_404(component_id)
    component_types = ComponentType.query.all()  # Fetch all component types
    component_sizes = Size.query.all()  # Fetch all sizes
    component_statuses = Status.query.all()  # Fetch all statuses
    component_models = Model.query.all()
    type_rigging = RiggingType.query.all()
    # Obtener los registros de Rigging asociados a este componente
    riggings = Rigging.query.filter_by(component_id=component.id).order_by(Rigging.date.desc()).all()
    return render_template('show_component.html', component=component, riggings=riggings,
                           component_types=component_types, component_sizes=component_sizes,
                           component_statuses=component_statuses, component_models=component_models)



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
        return redirect(url_for('view_components'))
    component_types = ComponentType.query.all()
    component_sizes = Size.query.all()
    component_statuses = Status.query.all()
    component_models = Model.query.all()
    return render_template('add_component.html',
                            component_types=component_types,
                            component_sizes=component_sizes,
                            component_statuses=component_statuses,
                            component_models=component_models)

@app.route('/component/edit/<int:id>', methods=['GET', 'POST'])
def edit_component(id):
    component = Component.query.get_or_404(id)
    component_id = request.form.get('component_id')
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
        component_type = component.component_type.component_type

        db.session.commit()
        return redirect(url_for('view_components', component_type=component_type))

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

@app.route('/rig/<int:rig_id>')
@login_required
def show_rig(rig_id):
    rig = Rig.query.get_or_404(rig_id)
    riggings = Rigging.query.filter((Rigging.rig_id == rig_id) | (Rigging.serial_numbers == rig.rig_number)).order_by(Rigging.date.desc()).all()
    return render_template('show_rig.html', rig=rig, riggings=riggings)

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
                               available_aads=available_aads, rig=rig, _anchor='riggingTab')

@app.route('/rigging')
def list_rigging():
    rigging = Rigging.query.all()
    return render_template('rigging.html', rigging=rigging)


@app.route('/rigging/add', methods=['GET', 'POST'])
@app.route('/rigging/add/component/<int:component_id>', methods=['GET', 'POST'])
@login_required
def rigging_add(component_id=None):
    if request.method == 'POST':
        date = request.form.get('date')
        type_rigging_id = request.form.get('type_rigging')  # Obtienes el ID
        type_rigging = RiggingType.query.get(type_rigging_id)  # Conviertes el ID a la instancia de RiggingType
        selected_value = request.form.get('serial_numbers')
        serial_numbers = ''

        rig_id = None
        component_id = component_id or None

        if component_id:
            component = Component.query.get(int(component_id))
            if component:
                serial_numbers = component.serial_number
                component_id = component.id
        else:
            selection_type, selection_id = selected_value.split('-')

            if selection_type == "Component":
                component = Component.query.get(int(selection_id))
                serial_numbers = component.serial_number
                if component:
                    component_id = component.id
            elif selection_type == "Rig":
                rig = Rig.query.get(int(selection_id))
                serial_numbers = rig.rig_number
                if rig:
                    rig_id = rig.id

        rigger_id = current_user.id if 'rigger' in [role.name for role in current_user.roles] else None

        if rig_id or component_id:
            new_rigging = Rigging(date=date, serial_numbers=serial_numbers, rig_id=rig_id,
                                  component_id=component_id, rigger_id=rigger_id, type_rigging=type_rigging)
            db.session.add(new_rigging)
            db.session.commit()
            flash('Rigging añadido correctamente.', 'success')
        else:
            flash('Error al añadir Rigging: valor seleccionado inválido.', 'danger')

        return redirect(url_for('list_rigging'))

    components = Component.query.all() if not component_id else [Component.query.get(int(component_id))]
    rigs = Rig.query.all()
    rigging_types = RiggingType.query.all()  # Obtienes todos los tipos de rigging
    return render_template('add_rigging.html', components=components, rigs=rigs,
                           rigging_types=rigging_types, preselected_component_id=component_id)



@app.route('/rigging/edit/<int:rigging_id>', methods=['GET', 'POST'])
@login_required
def edit_rigging(rigging_id):
    rigging = Rigging.query.get_or_404(rigging_id)

    if request.method == 'POST':
        date = request.form.get('date')
        type_rigging_id = request.form.get('type_rigging')
        description = request.form.get('description')
        selected_value = request.form.get('serial_numbers')

        rig_id = None
        component_id = None

        if selected_value:  # Asegúrate de que selected_value no esté vacío
            selection_type, selection_id = selected_value.split('-')

            if selection_type == "Component":
                component = Component.query.get(int(selection_id))
                if component:
                    rigging.serial_numbers = component.serial_number
                    component_id = component.id
            elif selection_type == "Rig":
                rig = Rig.query.get(int(selection_id))
                if rig:
                    rigging.serial_numbers = rig.rig_number
                    rig_id = rig.id

        rigging.date = date
        #rigging.type_rigging = RiggingType[type_rigging] if type_rigging in RiggingType.__members__ else None
        rigging_type = RiggingType.query.get(int(type_rigging_id))
        if rigging_type:
            rigging.type_rigging = rigging_type  # Asignar la instancia, no el ID

        rigging.description = description
        rigging.component_id = component_id
        rigging.rig_id = rig_id

        db.session.commit()
        flash('Rigging actualizado correctamente.', 'success')
        return redirect(url_for('view_components', _anchor='riggingTab'))

    components = Component.query.all()
    rigs = Rig.query.all()
    type_rigging = RiggingType.query.all()

    return render_template('edit_rigging.html', rigging=rigging, components=components,
                           rigs=rigs, type_rigging=type_rigging)



@app.route('/rigging/delete/<int:rigging_id>', methods=['POST'])
@login_required
def delete_rigging(rigging_id):
    rigging = Rigging.query.get_or_404(rigging_id)

    db.session.delete(rigging)
    db.session.commit()
    flash('Rigging eliminado correctamente.', 'success')

    return redirect(url_for('list_rigging'))


if __name__ == '__main__':
    app.run(debug=True)
