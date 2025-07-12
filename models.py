from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# 🚀 Base class for SQLAlchemy
Base = declarative_base()

# 📩 EmailStatus model
# 📩 EmailStatus model
class EmailStatus(Base):
    __tablename__ = 'email_status'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    sender = Column(String)
    classification = Column(String)
    summary = Column(String)
    timestamp = Column(DateTime)
    read = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    priority = Column(String(10), default='Low')
    smart_reply = Column(Text)
    body = Column(Text)
    attachments = Column(Text)   # ✅ Add this line


# 👤 User model
class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)              # Login email
    password = Column(String, nullable=False)                        # Hashed login password

    email_address = Column(String, nullable=False)                   # Gmail/IMAP address
    imap_password_encrypted = Column(String, nullable=False)         # Encrypted IMAP password

    role = Column(String, default='user')                            # Optional role string
    is_admin = Column(Boolean, default=False)                        # Admin access flag

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

# 📤 SentEmail model
class SentEmail(Base):
    __tablename__ = 'sent_emails'

    id = Column(Integer, primary_key=True)
    to = Column(String, nullable=False)
    cc = Column(String, nullable=True)
    bcc = Column(String, nullable=True)
    subject = Column(String)
    body = Column(Text)
    attachments = Column(Text, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    attachments = Column(String)
    

# 🔧 Database setup
engine = create_engine('sqlite:///emails.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
