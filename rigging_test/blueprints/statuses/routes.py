from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models.models import Component, ComponentType, Size, Status, Model, RiggingType, Rigging, Manufacturer
from extensions import db

statuses_bp = Blueprint('statuses', __name__)

@statuses_bp.route('/statuses')
def view_statuses():
    statuses = Status.query.all()
    return render_template('statuses/view_statuses.html', statuses=statuses)


@statuses_bp.route('/status/add', methods=['GET', 'POST'])
def add_status():
    message = None
    if request.method == 'POST':
        new_status = Status(status=request.form['status'])
        db.session.add(new_status)
        db.session.commit()
        message = "New status added successfully."
    return redirect(url_for('statuses.view_statuses'))


@statuses_bp.route('/status/edit/<int:id>', methods=['GET', 'POST'])
def edit_status(id):
    status = Status.query.get_or_404(id)
    if request.method == 'POST':
        status.status = request.form['status']
        db.session.commit()
        return redirect(url_for('view_statuses'))
    return render_template('statuses/edit_status.html', status=status)


@statuses_bp.route('/status/delete/<int:id>', methods=['POST'])
def delete_status(id):
    status = Status.query.get_or_404(id)
    db.session.delete(status)
    db.session.commit()
    return redirect(url_for('statuses.view_statuses'))