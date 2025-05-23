from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from flask_login import login_required, current_user
from datetime import datetime
import uuid
from models import db_session, Account, Transaction, TransactionCategory, Notification, TransactionType, AccountType

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

# Routes
@transactions_bp.route('/')
@login_required
def transactions_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = db_session.query(Transaction).filter_by(user_id=current_user.id).order_by(Transaction.date.desc())
    
    total = query.count()
    transactions = query.offset((page - 1) * per_page).limit(per_page).all()

    return render_template('transactions.html', transactions=transactions, page=page, total=total, per_page=per_page)

@transactions_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'POST':
        from_account_id = request.form.get("from_account_id")
        to_account_id = request.form.get("to_account_id")
        transaction_type = request.form.get("transaction_type")
        amount = float(request.form.get("amount", 0))
        description = request.form.get("description")

        # Retrieve from and to account
        from_account = Account.query.get(from_account_id)
        to_account = Account.query.get(to_account_id) if to_account_id else None

        # Validations
        if not from_account or from_account.user_id != current_user.id:
            flash("Invalid from account.", "danger")
            return redirect(url_for('transactions.new_transaction'))

        if transaction_type in ['transfer', 'payment']:
            if not to_account:
                flash("You must select a valid recipient account.", "danger")
                return redirect(url_for('transactions.new_transaction'))
            if from_account.id == to_account.id:
                flash("You cannot transfer to the same account.", "danger")
                return redirect(url_for('transactions.new_transaction'))

        if transaction_type in ['withdrawal', 'transfer', 'payment'] and from_account.balance < amount:
            flash("Insufficient balance.", "danger")
            return redirect(url_for('transactions.new_transaction'))

        # Perform balance update
        if transaction_type == 'deposit':
            from_account.balance += amount
        elif transaction_type in ['withdrawal', 'transfer', 'payment']:
            from_account.balance -= amount
            if to_account:
                to_account.balance += amount

        # Create transaction record
        transaction = Transaction(
            user_id=current_user.id,
            from_account_id=from_account.id,
            to_account_id=to_account.id if to_account else None,
            amount=amount,
            transaction_type=TransactionType(transaction_type),
            description=description,
            date=datetime.utcnow(),
            reference_number=str(uuid.uuid4())[:8],  # Generating a unique reference number
            status="completed"
        )

        # Commit the transaction to the database
        db_session.add(transaction)
        db_session.commit()
        flash("Transaction completed successfully.", "success")
        return redirect(url_for('dashboard'))

    # On GET: show form
    from_accounts = Account.query.filter_by(user_id=current_user.id, is_active=True).all()
    to_accounts = Account.query.filter(Account.is_active == True).all()
    categories = TransactionCategory.query.all()
    
    # Debug: Print account information to verify data
    print(f"New Transaction - From accounts: {[(a.id, a.name, a.account_number, a.is_active) for a in from_accounts]}")
    print(f"New Transaction - To accounts: {[(a.id, a.name, a.account_number, a.is_active) for a in to_accounts]}")
    
    return render_template(
        'new_transaction.html',
        from_accounts=from_accounts,
        to_accounts=to_accounts,
        categories=categories
    )

@transactions_bp.route('/accounts')
@login_required
def accounts_list():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    print(f"Accounts List - User accounts: {[(a.id, a.name, a.account_number, a.is_active) for a in accounts]}")
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
            balance=0.0,
            is_active=True
        )
        
        db_session.add(account)
        db_session.commit()
        
        flash('Account created successfully')
        return redirect(url_for('transactions.accounts_list'))
    
    return render_template('new_account.html')

@transactions_bp.route('/accounts/update/<int:account_id>', methods=['POST'])
@login_required
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    
    # Ensure the account belongs to the current user
    if account.user_id != current_user.id:
        flash('You do not have permission to update this account', 'danger')
        return redirect(url_for('transactions.accounts_list'))
    
    # Update account name if provided
    name = request.form.get('name')
    if name:
        account.name = name
    
    # Update active status if provided
    is_active = request.form.get('is_active')
    if is_active is not None:
        account.is_active = is_active == 'true'
    
    db_session.commit()
    flash('Account updated successfully')
    return redirect(url_for('transactions.accounts_list'))

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
