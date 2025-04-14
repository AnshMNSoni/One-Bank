from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user
from datetime import datetime
import uuid
from models import db_session, Account, Transaction, TransactionCategory, Notification, TransactionType, AccountType

transactions_bp = Blueprint('transactions', __name__)

# Routes
@transactions_bp.route('/transactions')
@login_required
def transactions_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = db_session.query(Transaction).filter_by(user_id=current_user.id).order_by(Transaction.date.desc())
    
    total = query.count()
    transactions = query.offset((page - 1) * per_page).limit(per_page).all()

    return render_template('transactions.html', transactions=transactions, page=page, total=total, per_page=per_page)

@transactions_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'POST':
        transaction_type = request.form.get('transaction_type')
        from_account_id = request.form.get('from_account_id')
        to_account_id = request.form.get('to_account_id')
        amount = float(request.form.get('amount'))
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        
        # Validate transaction
        from_account = Account.query.get(from_account_id)
        
        if not from_account or from_account.user_id != current_user.id:
            flash('Invalid account')
            return redirect(url_for('transactions.new_transaction'))
        
        if transaction_type in ['withdrawal', 'transfer'] and from_account.balance < amount:
            flash('Insufficient funds')
            return redirect(url_for('transactions.new_transaction'))
        
        # Generate reference number
        reference_number = str(uuid.uuid4())[:8].upper()
    
        # Create transaction
        transaction = Transaction(
            user_id=current_user.id,
            from_account_id=from_account_id,
            to_account_id=to_account_id if transaction_type == 'transfer' else None,
            amount=amount,
            transaction_type=TransactionType(transaction_type),
            category_id=category_id,
            description=description,
            reference_number=reference_number
        )
        
        # Update account balances
        if transaction_type == 'deposit':
            from_account.balance += amount
        elif transaction_type == 'withdrawal':
            from_account.balance -= amount
        elif transaction_type == 'transfer':
            from_account.balance -= amount
            to_account = Account.query.get(to_account_id)
            if to_account:
                to_account.balance += amount
        
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            title=f'New {transaction_type.capitalize()}',
            message=f'You have made a {transaction_type} of ${amount:.2f}',
            notification_type='info'
        )
        
        db_session.add(transaction)
        db_session.add(notification)
        db_session.commit()
        
        flash(f'{transaction_type.capitalize()} completed successfully')
        return redirect(url_for('transactions.transactions_list'))
    
    accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    categories = TransactionCategory.query.all()
    
    return render_template('new_transaction.html', accounts=accounts, categories=categories)

@transactions_bp.route('/accounts')
@login_required
def accounts_list():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('account.html', accounts=accounts)

@transactions_bp.route('/accounts/new', methods=['GET', 'POST'])
@login_required
def new_account():
    if request.method == 'POST':
        account_type = request.form.get('account_type')
        name = request.form.get('name')
        
        # Generate account number
        import random
        account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        
        account = Account(
            user_id=current_user.id,
            account_number=account_number,
            account_type=AccountType(account_type),
            name=name,
            balance=0.0
        )
        
        db_session.add(account)
        db_session.commit()
        
        flash('Account created successfully')
        return redirect(url_for('transactions.accounts_list'))
    
    return render_template('new_account.html')

@transactions_bp.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    
    # Mark notifications as read
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
    
    db_session.commit()
    
    return render_template('notifications.html', notifications=notifications)
