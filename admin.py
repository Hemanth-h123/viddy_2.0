from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Download, Subscription, Feedback, SiteStats
from datetime import datetime, timedelta
from sqlalchemy import func

admin = Blueprint('admin', __name__)

@admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    # Get user statistics
    total_users = User.query.count()
    active_users = User.query.join(Download).filter(
        Download.created_at > datetime.utcnow() - timedelta(days=7)
    ).distinct().count()
    
    # Get subscription statistics
    subscriptions = db.session.query(
        Subscription.plan_type, 
        func.count(Subscription.id)
    ).group_by(Subscription.plan_type).all()
    
    # Get download statistics
    total_downloads = Download.query.count()
    recent_downloads = Download.query.filter(
        Download.created_at > datetime.utcnow() - timedelta(days=7)
    ).count()
    
    # Get platform statistics
    platforms = db.session.query(
        Download.platform, 
        func.count(Download.id)
    ).group_by(Download.platform).all()
    
    # Get feedback statistics
    total_feedback = Feedback.query.count()
    unresolved_feedback = Feedback.query.filter_by(is_resolved=False).count()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        active_users=active_users,
        subscriptions=subscriptions,
        total_downloads=total_downloads,
        recent_downloads=recent_downloads,
        platforms=platforms,
        total_feedback=total_feedback,
        unresolved_feedback=unresolved_feedback
    )

@admin.route('/users')
@login_required
def users():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/feedback')
@login_required
def feedback():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    feedback = Feedback.query.order_by(Feedback.created_at.desc()).all()
    return render_template('admin/feedback.html', feedback=feedback)

@admin.route('/feedback/<int:id>', methods=['GET', 'POST'])
@login_required
def feedback_detail(id):
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    feedback = Feedback.query.get_or_404(id)
    
    if request.method == 'POST':
        feedback.admin_response = request.form.get('response')
        feedback.is_resolved = True if request.form.get('resolve') else False
        db.session.commit()
        flash('Feedback updated successfully.')
        return redirect(url_for('admin.feedback'))
    
    return render_template('admin/feedback_detail.html', feedback=feedback)

@admin.route('/downloads')
@login_required
def downloads():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.')
        return redirect(url_for('index'))
    
    downloads = Download.query.order_by(Download.created_at.desc()).limit(100).all()
    return render_template('admin/downloads.html', downloads=downloads)