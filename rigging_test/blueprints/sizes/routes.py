from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import Component, ComponentType, Size, Status, Model, RiggingType, Rigging, Manufacturer
from extensions import db

sizes_bp = Blueprint('sizes', __name__)

@sizes_bp.route('/sizes')
def view_sizes():
    sizes = Size.query.all()
    return render_template('sizes/view_sizes.html', sizes=sizes)


@sizes_bp.route('/size/add', methods=['GET', 'POST'])
def add_size():
    message = None
    if request.method == 'POST':
        new_size = Size(size=request.form['size'])
        db.session.add(new_size)
        db.session.commit()
        message = "New size added successfully."
    return redirect(url_for('sizes.view_sizes'))


@sizes_bp.route('/size/edit/<int:id>', methods=['GET', 'POST'])
def edit_size(id):
    size = Size.query.get_or_404(id)
    if request.method == 'POST':
        size.size = request.form['size']
        db.session.commit()
        return redirect(url_for('sizes.view_sizes'))
    return render_template('sizes/edit_size.html', size=size)


@sizes_bp.route('/size/delete/<int:id>', methods=['POST'])
def delete_size(id):
    size = Size.query.get_or_404(id)
    db.session.delete(size)
    db.session.commit()
    return redirect(url_for('sizes.view_sizes'))