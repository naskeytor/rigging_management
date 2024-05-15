from models.models import RiggingType, Rig, Rigging, Component
from utilities import prepare_component_data

def inject_rigging_types():
    rigging_types = RiggingType.query.all()
    return dict(rigging_types=rigging_types)

def inject_rigs():
    rigs = Rig.query.all()
    return dict(rigs=rigs)

def inject_rigging():
    rigging = Rigging.query.all()
    return dict(rigging=rigging)

def inject_rigging_components(component_id=None):
    components = Component.query.all() if not component_id else [Component.query.get(int(component_id))]
    return dict(components=components)

def inject_component_processor():
    available_canopies, available_containers, available_reserves, available_aads = prepare_component_data()
    return {
        'available_canopies': available_canopies,
        'available_containers': available_containers,
        'available_reserves': available_reserves,
        'available_aads': available_aads
    }
