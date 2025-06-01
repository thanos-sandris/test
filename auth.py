from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Form validation
        if not username or not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or email already exists', 'danger')
            return render_template('register.html')
            
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            is_admin=False,
            is_approved=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please wait for admin approval before logging in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
            
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
            
        if not user.is_approved and not user.is_admin:
            flash('Your account is pending approval by an administrator', 'warning')
            return render_template('login.html')
            
        login_user(user)
        next_page = request.args.get('next')
        
        if user.is_admin:
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            return redirect(next_page or url_for('quiz.list'))
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
