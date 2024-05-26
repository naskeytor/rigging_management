from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import Component, ComponentType, Size, Status, Model, RiggingType, Rigging, Manufacturer
from extensions import db

manufacturers_bp = Blueprint('manufacturers', __name__)

@manufacturers_bp.route('/manufacturers')
def view_manufacturers():
    manufacturers = Manufacturer.query.all()
    return render_template('manufacturers/view_manufacturers.html', manufacturers=manufacturers)


@manufacturers_bp.route('/manufacturer/add', methods=['GET', 'POST'])
def add_manufacturer():
    message = None
    if request.method == 'POST':
        # Handle the form submission
        new_manufacturer = Manufacturer(manufacturer=request.form['manufacturer'])
        db.session.add(new_manufacturer)
        db.session.commit()
        message = "New manufacturer added successfully."
    return redirect(url_for('manufacturers.view_manufacturers'))


@manufacturers_bp.route('/manufacturer/edit/<int:id>', methods=['GET', 'POST'])
def edit_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    if request.method == 'POST':
        manufacturer.manufacturer = request.form['manufacturer']
        db.session.commit()
        return redirect(url_for('view_manufacturers'))
    return render_template('manufacturers/edit_manufacturer.html', manufacturer=manufacturer)


@manufacturers_bp.route('/manufacturer/delete/<int:id>', methods=['POST'])
def delete_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    db.session.delete(manufacturer)
    db.session.commit()
    return redirect(url_for('manufacturers.view_manufacturers'))