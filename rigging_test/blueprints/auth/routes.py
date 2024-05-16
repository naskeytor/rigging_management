from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from models.models import User, Role
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)

        role = Role.query.filter_by(name='user').first()
        if not role:
            role = Role(name='user')
            db.session.add(role)
            db.session.commit()

        user.roles.append(role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Nombre de usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        return redirect(url_for('main.index'))
    return render_template('admin_dashboard.html')

