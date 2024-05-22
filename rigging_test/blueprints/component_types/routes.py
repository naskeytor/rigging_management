from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import Component, ComponentType, Size, Status, Model, RiggingType, Rigging
from extensions import db

component_types_bp = Blueprint('component_types', __name__)

@component_types_bp.route('/component_types')
def view_component_types():
    component_types = ComponentType.query.all()
    return render_template('component_types/view_component_types.html', component_types=component_types)


@component_types_bp.route('/component_type/add', methods=['GET', 'POST'])
def add_component_type():
    message = None
    if request.method == 'POST':
        new_type = ComponentType(component_type=request.form['component_type'])
        db.session.add(new_type)
        db.session.commit()
        return redirect(url_for('component_types.view_component_types'))
    return render_template('component_types/add_component_type.html', message=message)


@component_types_bp.route('/component_type/edit/<int:id>', methods=['GET', 'POST'])
def edit_component_type(id):
    component_type = ComponentType.query.get_or_404(id)
    if request.method == 'POST':
        component_type.component_type = request.form['component_type']
        db.session.commit()
        return redirect(url_for('view_component_types'))
    return render_template('component_types/edit_component_type.html', component_type=component_type)


@component_types_bp.route('/component_type/delete/<int:id>', methods=['POST'])
def delete_component_type(id):
    component_type = ComponentType.query.get_or_404(id)
    db.session.delete(component_type)
    db.session.commit()
    return redirect(url_for('component_types.view_component_types'))