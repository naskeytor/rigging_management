from models.models import ComponentType, Component


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