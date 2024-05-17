from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models.models import Component, ComponentType, Size, Status, Model, RiggingType, Rigging, Manufacturer, Rig, User
from extensions import db

rigging_bp = Blueprint('rigging', __name__)


@rigging_bp.route('/rigging')
def list_rigging():
    rigging = Rigging.query.all()
    return render_template('rigging/rigging.html', rigging=rigging)


@rigging_bp.route('/rigging/<int:rigging_id>')
@login_required
def show_rigging(rigging_id):
    rigging = Rigging.query.get_or_404(rigging_id)
    rigging_date = rigging.date
    rigging_rigger = rigging.rigger
    type_rigging = rigging.type_rigging
    serial_number = rigging.serial_numbers
    component_type = rigging.component
    description = rigging.description

    return render_template('rigging/show_rigging.html', rigging=rigging,
                           rigging_date=rigging_date, rigging_rigger=rigging_rigger,
                           type_rigging=type_rigging, serial_number=serial_number, component_type=component_type,
                           description=description)


@rigging_bp.route('/rigging/add', methods=['GET', 'POST'])
@rigging_bp.route('/rigging/add/<int:component_id>', methods=['GET', 'POST'])
@login_required
def rigging_add(component_id=None):
    if request.method == 'POST':
        date = request.form.get('date')
        type_rigging_id = request.form.get('type_rigging')
        type_rigging = RiggingType.query.get(type_rigging_id)
        selected_value = request.form.get('serial_numbers')
        description = request.form.get('description')
        serial_numbers = ''
        rig_id = request.form.get('rig_id')

        # Maneja el caso donde component_id es proporcionado como parámetro de URL
        if component_id:
            component = Component.query.get(int(component_id))
            if component:
                serial_numbers = component.serial_number
                rig_id = None  # Asegúrate de que rig_id es None si se proporciona component_id
        elif selected_value:
            selection_type, selection_id = selected_value.split('-')

            if selection_type == "Component":
                component = Component.query.get(int(selection_id))
                serial_numbers = component.serial_number
                if component:
                    component_id = component.id
                    rig_id = None  # Asegúrate de que rig_id es None si se selecciona un componente
            elif selection_type == "Rig":
                rig = Rig.query.get(int(selection_id))
                serial_numbers = rig.rig_number
                if rig:
                    rig_id = rig.id
                    component_id = None  # Asegúrate de que component_id es None si se selecciona un rig

        rigger_id = current_user.id if 'rigger' in [role.name for role in current_user.roles] else None

        if rig_id or component_id:
            new_rigging = Rigging(
                date=date,
                serial_numbers=serial_numbers,
                rig_id=rig_id,
                description=description,
                component_id=component_id,
                rigger_id=rigger_id,
                type_rigging=type_rigging
            )
            db.session.add(new_rigging)
            db.session.commit()
        else:
            flash('Error al añadir Rigging: valor seleccionado inválido.', 'danger')

        if rig_id:
            return redirect(url_for('rigs.show_rig', rig_id=rig_id))
        elif component_id:
            return redirect(url_for('components.show_component', component_id=component_id))

    components = Component.query.all() if not component_id else [Component.query.get(int(component_id))]
    rigs = Rig.query.all()
    rigging_types = RiggingType.query.all()
    return render_template('index.html', components=components, rigs=rigs,
                           rigging_types=rigging_types, preselected_component_id=component_id)



@rigging_bp.route('/rigging/edit/<int:rigging_id>', methods=['GET', 'POST'])
@login_required
def edit_rigging(rigging_id):
    rigging = Rigging.query.get_or_404(rigging_id)
    if request.method == 'POST':
        date = request.form.get('date')
        type_rigging_id = request.form.get('type_rigging')
        description = request.form.get('description')
        selected_value = request.form.get('serial_numbers')

        rig_id = None
        component_id = rigging.component.id if rigging.component else None

        if selected_value:
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
        rigging.description = description
        rigging.component_id = component_id
        rigging.rig_id = rig_id

        if type_rigging_id:
            try:
                type_rigging_id = int(type_rigging_id)
                rigging_type = RiggingType.query.get(type_rigging_id)
                if rigging_type:
                    rigging.type_rigging = rigging_type
                else:
                    flash('Tipo de rigging no encontrado.', 'error')
                    return redirect(url_for('rigging.edit_rigging', rigging_id=rigging_id))
            except ValueError:
                flash('ID de tipo de rigging inválido.', 'error')
                return redirect(url_for('rigging.edit_rigging', rigging_id=rigging_id))
        else:
            flash('ID de tipo de rigging no proporcionado.', 'error')
            return redirect(url_for('rigging.edit_rigging', rigging_id=rigging_id))

        db.session.commit()
        flash('Rigging actualizado correctamente.', 'success')
        return redirect(url_for('components.view_components', _anchor='riggingTab'))

    components = Component.query.all()
    rigs = Rig.query.all()
    rigging_types = RiggingType.query.all()

    return render_template('rigging/edit_rigging.html', rigging=rigging, components=components,
                           rigs=rigs, rigging_types=rigging_types)


@rigging_bp.route('/rigging/delete/<int:rigging_id>', methods=['POST'])
@login_required
def delete_rigging(rigging_id):
    rigging = Rigging.query.get_or_404(rigging_id)

    db.session.delete(rigging)
    db.session.commit()
    flash('Rigging eliminado correctamente.', 'success')

    return redirect(url_for('rigging.list_rigging'))
