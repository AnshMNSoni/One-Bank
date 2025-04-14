from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from models import db_session, User, UserProfile, LoginHistory

auth_bp = Blueprint('auth', __name__)

# Routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            
            # Log failed login attempt
            login_history = LoginHistory(
                user_id=user.id if user else None,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                is_successful=False
            )
            db_session.add(login_history)
            db_session.commit()
            
            return redirect(url_for('auth.login'))
        
        login_user(user)
        
        # Log successful login
        login_history = LoginHistory(
            user_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db_session.add(login_history)
        db_session.commit()
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('dashboard')
        return redirect(next_page)
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Create user profile
        profile = UserProfile(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            phone_number=request.form.get('phone_number'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            zip_code=request.form.get('zip_code')
        )
        
        user.profile = profile
        
        db_session.add(user)
        db_session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        # Update user account information
        current_user.username = request.form.get('username')
        current_user.email = request.form.get('email')
        
        if request.form.get('password'):
            current_user.set_password(request.form.get('password'))
        
        db_session.commit()
        flash('Account updated successfully')
        return redirect(url_for('auth.account'))
    
    return render_template('account.html')
