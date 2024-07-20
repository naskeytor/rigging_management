from rigging_test.models.models import ComponentType, Component
from rigging_test.extensions import db
from rigging_test.models.models import Component, Rig, rig_component_association


def find_component_by_serial(serial_number, component_type_name):
    component_type = ComponentType.query.filter_by(component_type=component_type_name).first()
    if not component_type:
        return None
    component = Component.query.filter_by(serial_number=serial_number, component_type_id=component_type.id).first()
    return component

def prepare_component_data():
    # Supongamos que cada tipo de componente tiene un ID único asociado en la base de datos.
    # Primero, obtendríamos los IDs para cada tipo de componente.
    canopy_type_id = ComponentType.query.filter_by(component_type='Canopy').first().id
    container_type_id = ComponentType.query.filter_by(component_type='Container').first().id
    reserve_type_id = ComponentType.query.filter_by(component_type='Reserve').first().id
    aad_type_id = ComponentType.query.filter_by(component_type='Aad').first().id

    # Luego, basándonos en esos IDs, filtraríamos los componentes disponibles por tipo.
    available_canopies = Component.query.filter_by(component_type_id=canopy_type_id, rigs=None).all()
    available_containers = Component.query.filter_by(component_type_id=container_type_id, rigs=None).all()
    available_reserves = Component.query.filter_by(component_type_id=reserve_type_id, rigs=None).all()
    available_aads = Component.query.filter_by(component_type_id=aad_type_id, rigs=None).all()


    # Devolvemos los conjuntos de datos para cada tipo de componente.
    return available_canopies, available_containers, available_reserves, available_aads

def umount_component_logic(component_id, current_aad_jumps):
    component = Component.query.get_or_404(component_id)
    rig_id = None
    for rig in component.rigs:
        rig_id = rig.id
        break

    if component.component_type.component_type in ['Canopy', 'Container'] and current_aad_jumps is not None:
        component.jumps += (current_aad_jumps - component.aad_jumps_on_mount)
        component.aad_jumps_on_mount = 0
    elif component.component_type.component_type in ['Aad'] and current_aad_jumps is not None:
        for rig in component.rigs:
            for comp in rig.components:
                if comp.component_type.component_type in ['Canopy', 'Container']:
                    comp.jumps += current_aad_jumps - comp.aad_jumps_on_mount
                    db.session.add(comp)
                elif comp.component_type.component_type in ['Aad']:
                    comp.jumps += current_aad_jumps

    if rig_id:
        stmt = rig_component_association.delete().where(
            rig_component_association.c.rig_id == rig_id,
            rig_component_association.c.component_id == component_id
        )
        db.session.execute(stmt)
        db.session.commit()

def mount_component_logic(component_id, rig_id, current_aad_jumps):
    component = Component.query.get_or_404(component_id)
    rig = Rig.query.get_or_404(rig_id)

    if component.component_type.component_type in ['Canopy', 'Container', 'Aad']:
        if current_aad_jumps is not None:
            component.aad_jumps_on_mount = current_aad_jumps

    rig.components.append(component)
    db.session.commit()