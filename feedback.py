from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Feedback

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not subject or not message:
            flash('Please fill in all fields.')
            return redirect(url_for('feedback.submit'))
        
        user_id = current_user.id if current_user.is_authenticated else None
        
        feedback = Feedback(
            subject=subject,
            message=message,
            user_id=user_id
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!')
        return redirect(url_for('index'))
    
    return render_template('feedback/submit.html')

@feedback_bp.route('/my-feedback')
@login_required
def my_feedback():
    feedback = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    return render_template('feedback/my_feedback.html', feedback=feedback)