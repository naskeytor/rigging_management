from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from extensions import db
from models.models import Model, Manufacturer


models_bp = Blueprint('models', __name__)

@models_bp.route('/models', methods=['GET'])
def view_models():
    models = Model.query.all()
    return render_template('models/view_models.html', models=models)

@models_bp.route('/model/add', methods=['GET', 'POST'])
def add_model():
    if request.method == 'POST':
        model_name = request.form['model']
        manufacturer_id = request.form['manufacturer_id']
        new_model = Model(model=model_name, manufacturer_id=manufacturer_id)
        db.session.add(new_model)
        db.session.commit()
        flash('New model added successfully.', 'success')
        return redirect(url_for('models.view_models'))

    manufacturers = Manufacturer.query.all()
    return redirect(url_for('models.view_models'))

@models_bp.route('/model/edit/<int:id>', methods=['GET', 'POST'])
def edit_model(id):
    model = Model.query.get_or_404(id)
    if request.method == 'POST':
        model.model = request.form['model']
        model.manufacturer_id = request.form['manufacturer_id']
        db.session.commit()
        flash('Model updated successfully.', 'success')
        return redirect(url_for('models.view_models'))

    manufacturers = Manufacturer.query.all()
    return render_template('models/edit_model.html', model=model, manufacturers=manufacturers)

@models_bp.route('/model/delete/<int:id>', methods=['POST'])
def delete_model(id):
    model = Model.query.get_or_404(id)
    db.session.delete(model)
    db.session.commit()
    flash('Model deleted successfully.', 'success')
    return redirect(url_for('models.view_models'))
