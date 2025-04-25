from flask import Flask, render_template, redirect, url_for, flash, request, g
from flask_login import LoginManager, current_user, login_required
from datetime import datetime

from config import Config
from models import db_session, Base, User, init_db
from auth import auth_bp
from transactions import transactions_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(transactions_bp)

@app.before_request
def before_request():
    g.user = current_user
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db_session.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    from models import Account, Transaction

    # Show only current user's active accounts as 'from' accounts
    from_accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    print(f"Dashboard - From accounts: {[(a.id, a.name, a.account_number) for a in from_accounts]}")

    # Show all active accounts (including other users) as 'to' accounts
    to_accounts = Account.query.filter(Account.is_active == True).all()
    print(f"Dashboard - To accounts: {[(a.id, a.name, a.account_number) for a in to_accounts]}")
    
    # Add this line to pass the user's accounts to the template for balance summary
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    print(f"Dashboard - All user accounts: {[(a.id, a.name, a.account_number, a.is_active) for a in accounts]}")
    
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        from_accounts=from_accounts,
        to_accounts=to_accounts,
        recent_transactions=recent_transactions,
        accounts=accounts
    )

@app.route('/profile')
@login_required
def profile():
    from models import UserProfile
    user_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('profile.html', profile=user_profile)

@app.route('/instant-loan')
@login_required
def instant_loan():
    return render_template('instant_loan.html')

@app.route('/secure-transactions')
@login_required
def secure_transactions():
    return render_template('secure_transactions.html')

@app.route('/mobile-banking-guide')
@login_required
def mobile_banking_guide():
    return render_template('mobile_banking_guide.html')

@app.route('/financial-tracking')
@login_required
def financial_tracking():
    return render_template('financial_tracking.html')

@app.route('/seed-database')
def seed_database():
    from seed_db import seed_database
    seed_database()
    flash('Database has been seeded with sample data')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
