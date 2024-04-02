from app import app, db  # Asegúrate de importar 'app' y 'db' correctamente
from models import Rigging, RiggingType

with app.app_context():
    var = RiggingType.query.all()
    print(var)
