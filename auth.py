from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, Subscription, UserSettings, db
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('index'))
        
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
            
        # Check if username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.signup'))
            
        # Create new user
        new_user = User(email=email, username=username)
        new_user.set_password(password)
        
        # Create free subscription
        end_date = datetime.utcnow() + timedelta(days=30)  # 30-day free trial
        subscription = Subscription(plan_type='free', end_date=end_date)
        
        # Create default settings
        settings = UserSettings()
        
        # Add to database
        new_user.subscription = subscription
        new_user.settings = settings
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! You can now log in.')
        return redirect(url_for('auth.login'))
        
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@auth.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        settings = current_user.settings
        
        settings.preferred_quality = request.form.get('preferred_quality')
        settings.auto_download = True if request.form.get('auto_download') else False
        settings.notifications_enabled = True if request.form.get('notifications_enabled') else False
        settings.theme = request.form.get('theme')
        
        db.session.commit()
        flash('Settings updated successfully!')
        
    return render_template('settings.html', user=current_user)