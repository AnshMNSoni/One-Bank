from models import db_session, User, UserProfile, Account, AccountType, TransactionCategory
from werkzeug.security import generate_password_hash
import random

def seed_database():
    print("Starting database seeding...")
    
    # Check if we already have users
    existing_users = User.query.all()
    if existing_users:
        print(f"Database already has {len(existing_users)} users")
        
        # Check if the first user has accounts
        first_user = existing_users[0]
        user_accounts = Account.query.filter_by(user_id=first_user.id).all()
        
        if user_accounts:
            print(f"User {first_user.username} already has {len(user_accounts)} accounts")
            
            # Print account details for debugging
            for account in user_accounts:
                print(f"Account ID: {account.id}, Name: {account.name}, Number: {account.account_number}, Type: {account.account_type.value}, Balance: ${account.balance}, Active: {account.is_active}")
            
            # Ensure accounts have names
            for account in user_accounts:
                if not account.name:
                    account_type = account.account_type.value.capitalize() if account.account_type else "Unknown"
                    account.name = f"{account_type} Account"
                    print(f"Updated account {account.id} with name: {account.name}")
            
            # Ensure accounts are active
            for account in user_accounts:
                if not account.is_active:
                    account.is_active = True
                    print(f"Activated account {account.id}")
            
            db_session.commit()
            print("Existing accounts updated")
            return
        else:
            print(f"User {first_user.username} has no accounts. Creating sample accounts...")
            create_sample_accounts(first_user.id)
            return
    
    # Create a test user if none exists
    print("No users found. Creating a test user...")
    test_user = User(
        username="testuser",
        email="test@example.com"
    )
    test_user.set_password("password")
    
    # Create user profile
    profile = UserProfile(
        first_name="Test",
        last_name="User",
        phone_number="555-123-4567",
        address="123 Main St",
        city="Anytown",
        state="CA",
        zip_code="12345"
    )
    
    test_user.profile = profile
    db_session.add(test_user)
    db_session.commit()
    print(f"Created test user with ID: {test_user.id}")
    
    # Create sample accounts for the test user
    create_sample_accounts(test_user.id)
    
    # Create transaction categories if they don't exist
    create_transaction_categories()
    
    print("Database seeding completed successfully")

def create_sample_accounts(user_id):
    # Create checking account
    checking = Account(
        user_id=user_id,
        account_number=generate_account_number(),
        account_type=AccountType.CHECKING,
        name="Checking Account",
        balance=2500.00,
        is_active=True
    )
    
    # Create savings account
    savings = Account(
        user_id=user_id,
        account_number=generate_account_number(),
        account_type=AccountType.SAVINGS,
        name="Savings Account",
        balance=10000.00,
        is_active=True
    )
    
    # Create credit account
    credit = Account(
        user_id=user_id,
        account_number=generate_account_number(),
        account_type=AccountType.CREDIT,
        name="Credit Card",
        balance=-500.00,
        is_active=True
    )
    
    # Create investment account
    investment = Account(
        user_id=user_id,
        account_number=generate_account_number(),
        account_type=AccountType.INVESTMENT,
        name="Investment Account",
        balance=5000.00,
        is_active=True
    )
    
    db_session.add_all([checking, savings, credit, investment])
    db_session.commit()
    
    print(f"Created 4 sample accounts for user ID: {user_id}")
    return [checking, savings, credit, investment]

def generate_account_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])

def create_transaction_categories():
    # Check if categories already exist
    existing_categories = TransactionCategory.query.all()
    if existing_categories:
        print(f"Found {len(existing_categories)} existing transaction categories")
        return
    
    # Create basic categories
    categories = [
        TransactionCategory(name="Groceries", description="Food and household items", icon="shopping-cart"),
        TransactionCategory(name="Utilities", description="Bills and utilities", icon="zap"),
        TransactionCategory(name="Entertainment", description="Movies, games, etc.", icon="film"),
        TransactionCategory(name="Dining", description="Restaurants and takeout", icon="coffee"),
        TransactionCategory(name="Transportation", description="Gas, public transit, etc.", icon="car"),
        TransactionCategory(name="Housing", description="Rent, mortgage, repairs", icon="home"),
        TransactionCategory(name="Healthcare", description="Medical expenses", icon="activity"),
        TransactionCategory(name="Education", description="Tuition, books, etc.", icon="book"),
        TransactionCategory(name="Shopping", description="Clothing, electronics, etc.", icon="shopping-bag"),
        TransactionCategory(name="Travel", description="Flights, hotels, etc.", icon="map"),
        TransactionCategory(name="Income", description="Salary, gifts, etc.", icon="dollar-sign"),
        TransactionCategory(name="Other", description="Miscellaneous expenses", icon="more-horizontal")
    ]
    
    db_session.add_all(categories)
    db_session.commit()
    print(f"Created {len(categories)} transaction categories")

if __name__ == "__main__":
    seed_database()
