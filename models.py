from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    downloads = db.relationship('Download', backref='user', lazy=True)
    subscription = db.relationship('Subscription', backref='user', lazy=True, uselist=False)
    feedback = db.relationship('Feedback', backref='user', lazy=True)
    settings = db.relationship('UserSettings', backref='user', lazy=True, uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False, default='free')  # free, basic, premium
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    payment_id = db.Column(db.String(128))
    
    def __repr__(self):
        return f'<Subscription {self.plan_type} for User {self.user_id}>'

class Download(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    platform = db.Column(db.String(50))
    file_path = db.Column(db.String(512))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Download {self.platform} by User {self.user_id}>'

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)
    admin_response = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Feedback by User {self.user_id}>'

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    preferred_quality = db.Column(db.String(20), default='high')  # low, medium, high
    auto_download = db.Column(db.Boolean, default=False)
    notifications_enabled = db.Column(db.Boolean, default=True)
    theme = db.Column(db.String(20), default='dark')  # light, dark
    
    def __repr__(self):
        return f'<Settings for User {self.user_id}>'

class SiteStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, unique=True)
    visits = db.Column(db.Integer, default=0)
    downloads = db.Column(db.Integer, default=0)
    signups = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Stats for {self.date}>'