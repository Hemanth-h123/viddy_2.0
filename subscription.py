from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Subscription
from datetime import datetime, timedelta
import os

# Lazy import Stripe to avoid startup failures when unavailable
try:
    import stripe  # type: ignore
except Exception:
    stripe = None

subscription = Blueprint('subscription', __name__)

# Initialize Stripe using environment variables; disable if not configured
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PRICE_BASIC = os.getenv("STRIPE_PRICE_BASIC")  # e.g., price_XXXXXXXX
STRIPE_PRICE_PREMIUM = os.getenv("STRIPE_PRICE_PREMIUM")

if stripe and STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Define subscription plans
SUBSCRIPTION_PLANS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'features': ['Basic video downloads', 'Standard quality', '5 downloads per day'],
        'stripe_price_id': None
    },
    'basic': {
        'name': 'Basic',
        'price': 4.99,
        'features': ['Unlimited downloads', 'HD quality', 'No ads', 'Faster downloads'],
        'stripe_price_id': STRIPE_PRICE_BASIC
    },
    'premium': {
        'name': 'Premium',
        'price': 9.99,
        'features': ['Everything in Basic', '4K quality', 'Priority support', 'Batch downloads'],
        'stripe_price_id': STRIPE_PRICE_PREMIUM
    }
}

@subscription.route('/plans')
def plans():
    return render_template('subscription/plans.html', plans=SUBSCRIPTION_PLANS, user=current_user)

@subscription.route('/checkout/<plan_type>')
@login_required
def checkout(plan_type):
    if plan_type not in SUBSCRIPTION_PLANS or plan_type == 'free':
        flash('Invalid subscription plan')
        return redirect(url_for('subscription.plans'))

    plan = SUBSCRIPTION_PLANS[plan_type]

    # Guard: Stripe must be available and configured
    if not stripe or not STRIPE_SECRET_KEY or not plan.get('stripe_price_id'):
        flash('Payments are not configured. Please try again later or choose the Free plan.')
        return redirect(url_for('subscription.plans'))

    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plan['stripe_price_id'],
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('subscription.success', plan_type=plan_type, _external=True),
            cancel_url=url_for('subscription.plans', _external=True),
            customer_email=current_user.email,
            client_reference_id=str(current_user.id)
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f'Error creating checkout session: {str(e)}')
        return redirect(url_for('subscription.plans'))

@subscription.route('/success/<plan_type>')
@login_required
def success(plan_type):
    if plan_type not in SUBSCRIPTION_PLANS:
        flash('Invalid subscription plan')
        return redirect(url_for('subscription.plans'))
    
    # Update user's subscription
    user_sub = current_user.subscription
    if not user_sub:
        user_sub = Subscription(user_id=current_user.id)
        db.session.add(user_sub)
    
    user_sub.plan_type = plan_type
    user_sub.start_date = datetime.utcnow()
    user_sub.end_date = datetime.utcnow() + timedelta(days=30)  # 30-day subscription
    user_sub.is_active = True
    
    db.session.commit()
    
    flash(f'Successfully subscribed to {SUBSCRIPTION_PLANS[plan_type]["name"]} plan!')
    return redirect(url_for('subscription.my_subscription'))

@subscription.route('/my-subscription')
@login_required
def my_subscription():
    return render_template('subscription/my_subscription.html', 
                          user=current_user, 
                          plans=SUBSCRIPTION_PLANS)

@subscription.route('/cancel')
@login_required
def cancel():
    user_sub = current_user.subscription
    if user_sub and user_sub.plan_type != 'free':
        # In a real implementation, you would also cancel the subscription in Stripe
        user_sub.plan_type = 'free'
        user_sub.is_active = True
        db.session.commit()
        flash('Your subscription has been cancelled. You have been downgraded to the free plan.')
    
    return redirect(url_for('subscription.my_subscription'))