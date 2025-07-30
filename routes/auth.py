from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.models import db, User

auth_bp = Blueprint('auth', __name__)

# ---------------- Login ----------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role

            flash(f"Welcome {user.full_name}!", "success")

            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))  # admin blueprint
            else:
                return redirect(url_for('user.dashboard'))   # user blueprint
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('login.html')


# ---------------- Register ----------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'warning')
            return render_template('register.html')

        new_user = User(username=username, password=password, full_name=full_name, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))  # ✅ Fixed

    return render_template('register.html')


# ---------------- Logout ----------------
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'info')
    return redirect(url_for('auth.login'))
