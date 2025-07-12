from app import db, User, fernet

# Find the admin user
admin = User.query.filter_by(email="admin@gmail.com").first()

if not admin:
    print("❌ Admin user not found.")
else:
    new_imap_password = "your_app_specific_password"  # No spaces!
    encrypted_password = fernet.encrypt(new_imap_password.encode()).decode()
    admin.imap_password_encrypted = encrypted_password
    db.session.commit()
    print("✅ Admin IMAP password updated successfully.")
