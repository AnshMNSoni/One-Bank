from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from flask_login import UserMixin
import enum

# Database setup
engine = create_engine('sqlite:///instance/records.db')
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Enums
class TransactionType(enum.Enum):
    DEPOSIT = 'deposit'
    WITHDRAWAL = 'withdrawal'
    TRANSFER = 'transfer'
    PAYMENT = 'payment'

class AccountType(enum.Enum):
    CHECKING = 'checking'
    SAVINGS = 'savings'
    CREDIT = 'credit'
    INVESTMENT = 'investment'

# Models
class User(UserMixin, Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    profile = relationship("UserProfile", backref="user", uselist=False)
    accounts = relationship("Account", backref="user")
    transactions = relationship("Transaction", backref="user")
    login_history = relationship("LoginHistory", backref="user")
    notifications = relationship("Notification", backref="user")
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    first_name = Column(String(64))
    last_name = Column(String(64))
    phone_number = Column(String(20))
    address = Column(String(256))
    city = Column(String(64))
    state = Column(String(64))
    zip_code = Column(String(20))
    date_of_birth = Column(DateTime)
    profile_picture = Column(String(256))
    
    def __repr__(self):
        return f'<UserProfile {self.first_name} {self.last_name}>'

class LoginHistory(Base):
    __tablename__ = 'login_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    login_time = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(256))
    is_successful = Column(Boolean, default=True)
    
    def __repr__(self):
        return f'<LoginHistory {self.user_id} at {self.login_time}>'

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    account_number = Column(String(20), unique=True, nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    name = Column(String(64))
    
    transactions_from = relationship("Transaction", foreign_keys="Transaction.from_account_id", backref="from_account")
    transactions_to = relationship("Transaction", foreign_keys="Transaction.to_account_id", backref="to_account")
    
    def __repr__(self):
        return f'<Account {self.account_number}>'

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    from_account_id = Column(Integer, ForeignKey('accounts.id'))
    to_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    category_id = Column(Integer, ForeignKey('transaction_categories.id'), nullable=True)
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(String(256))
    reference_number = Column(String(64), unique=True)
    status = Column(String(20), default='completed')
    
    category = relationship("TransactionCategory", backref="transactions")
    
    def __repr__(self):
        return f'<Transaction {self.reference_number}>'

class TransactionCategory(Base):
    __tablename__ = 'transaction_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256))
    icon = Column(String(64))
    
    def __repr__(self):
        return f'<TransactionCategory {self.name}>'

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(128), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    notification_type = Column(String(20), default='info')  # info, warning, alert
    
    def __repr__(self):
        return f'<Notification {self.id}>'

def init_db():
    Base.metadata.create_all(bind=engine)
