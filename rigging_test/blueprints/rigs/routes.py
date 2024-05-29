from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import Component, ComponentType, Size, Status, Model, RiggingType, Rigging, Rig
from extensions import db
from utilities import find_component_by_serial, prepare_component_data

rigs_bp = Blueprint('rigs', __name__)

@rigs_bp.route('/rigs')
def list_rigs():
    rigs = Rig.query.all()
    return render_template('rigs/rigs.html', rigs=rigs)


@rigs_bp.route('/rig/<int:rig_id>')
@login_required
def show_rig(rig_id):
    rig = Rig.query.get_or_404(rig_id)
    # Asumiendo que tienes relaciones como rig.canopy, rig.container, etc.
    canopy_serial = rig.canopy.serial_number if rig.canopy else "No asignado"
    container_serial = rig.container.serial_number if rig.container else "No asignado"
    reserve_serial = rig.reserve.serial_number if rig.reserve else "No asignado"
    aad_serial = rig.aad.serial_number if rig.aad else "No asignado"

    riggings = Rigging.query.filter((Rigging.rig_id == rig_id) | (Rigging.serial_numbers == rig.rig_number)).order_by(
        Rigging.date.desc()).all()

    return render_template('rigs/show_rig.html', rig=rig, riggings=riggings, canopy_serial=canopy_serial,
                           container_serial=container_serial, reserve_serial=reserve_serial, aad_serial=aad_serial)


@rigs_bp.route('/rigs/add', methods=['GET', 'POST'])
def add_rig():
    print("Request method:", request.method)
    if request.method == 'POST':
        rig_number = request.form.get('rig_number')

        # Verifica si el número de rig ya existe
        existing_rig = Rig.query.filter_by(rig_number=rig_number).first()
        if existing_rig:
            error_message = "El número de rig ya existe. Por favor, elige otro."
            # Renderiza nuevamente el formulario con el mensaje de error y los datos necesarios para el formulario
            return render_template('rigs/rigs.html', error_message=error_message)

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

        return redirect(url_for('rigs.list_rigs'))
    else:
        # Preparación de los datos necesarios para el formulario
        available_canopies, available_containers, available_reserves, available_aads = prepare_component_data()
        return render_template('index.html', available_canopies=available_canopies,
                               available_containers=available_containers, available_reserves=available_reserves,
                               available_aads=available_aads)


@rigs_bp.route('/rigs/delete/<int:rig_id>', methods=['POST'])
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
    return redirect(url_for('rigs.list_rigs'))


@rigs_bp.route('/rigs/edit/<int:rig_id>', methods=['GET', 'POST'])
def edit_rig(rig_id):
    rig = Rig.query.get_or_404(rig_id)
    if request.method == 'POST':
        rig_number = request.form.get('rig_number')
        existing_rig = Rig.query.filter_by(rig_number=rig_number).first()
        if existing_rig and existing_rig.id != rig.id:
            print("El número de rig ya existe. Por favor, elige otro.")
            return render_template('rigs/edit_rig.html', rig=rig)

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
        return redirect(url_for('rigs.list_rigs'))
    else:
        available_canopies, available_containers, available_reserves, available_aads = prepare_component_data()
        return render_template('rigs/edit_rig.html', available_canopies=available_canopies,
                               available_containers=available_containers, available_reserves=available_reserves,
                               available_aads=available_aads, rig=rig, _anchor='riggingTab')