from getpass import getpass
from werkzeug.security import generate_password_hash
from models import Session, User

# Prompt for admin credentials
email = input("Enter admin email: ")

# Secure password input
password = getpass("Enter password (hidden): ")
confirm_password = getpass("Confirm password: ")

if password != confirm_password:
    print("❌ Passwords do not match.")
    exit(1)

# Hash the password
hashed_password = generate_password_hash(password)

# Create admin user
session = Session()
existing_user = session.query(User).filter_by(email=email).first()

if existing_user:
    print("⚠️ User already exists.")
else:
    admin = User(email=email, password=hashed_password, is_admin=True)
    session.add(admin)
    session.commit()
    print("✅ Admin user created successfully.")

session.close()
