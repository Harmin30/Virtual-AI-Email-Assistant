from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from email.mime.text import MIMEText
from transformers import T5Tokenizer, T5ForConditionalGeneration, pipeline
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from dotenv import load_dotenv
import smtplib, os
# app = Flask(__name__)
from email_utils import fetch_emails
from models import Session, EmailStatus, User
# Compose Email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from flask import flash
from werkzeug.utils import secure_filename
from models import EmailStatus, User, SentEmail
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import LoginManager
from flask import send_from_directory
# from eva_voice import speak, listen
import threading
import time
from datetime import datetime
import dateparser
import sqlite3
import datetime
# Register adapter and converter for datetime
sqlite3.register_adapter(datetime.datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.datetime.fromisoformat(val.decode("utf-8")))
import sqlite3

DATABASE = 'emails.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


from flask import request, jsonify



# ------------------ Load Configuration ------------------
load_dotenv()
EMAIL = os.getenv('EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')


# ------------------ Flask App Setup ------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY
# Add these config lines for Remember Me cookie duration and security:
from datetime import timedelta

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)    # Remember me for 7 days (customize as needed)
app.config['REMEMBER_COOKIE_HTTPONLY'] = True                 # Protect cookie from JS access
app.config['REMEMBER_COOKIE_SECURE'] = False                   # Set True in production with HTTPS!
app.config['SESSION_COOKIE_SECURE'] = False                    # Same here: True in production with HTTPS
serializer = URLSafeTimedSerializer(app.secret_key)


# ------------------ Login Setup ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------ AI Setup ------------------
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")



# ------------------ Helper Functions ------------------

from email_helpers import categorize_email, assign_priority


# def extract_reminder_time(text):
#     reminder_time = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
#     if reminder_time and reminder_time > datetime.now():
#         return reminder_time.strftime("%Y-%m-%d %H:%M:%S")
#     return None




def generate_smart_reply(email_text):
    prompt = f"You're replying to this email:\n\n{email_text.strip()}\n\nWrite a short, polite reply."
    input_ids = tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=512)
    output_ids = model.generate(input_ids, max_new_tokens=80, temperature=0.7, do_sample=True)
    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

@app.template_filter('format_datetime')
def format_datetime(value):
    try:
        value = datetime.fromisoformat(value) if isinstance(value, str) else value
        return value.strftime('%b %d, %Y %I:%M %p')
    except:
        return value

from flask_login import login_required, current_user

@app.route('/test-admin')
@login_required
def test_admin():
    is_admin = getattr(current_user, 'is_admin', None)
    return (
        f"<p>User ID: {current_user.id}</p>"
        f"<p>Email: {current_user.email}</p>"
        f"<p>Is Admin (raw): {is_admin}</p>"
        f"<p>Is Admin (type): {type(is_admin)}</p>"
        f"<p>Is Admin (bool): {bool(is_admin)}</p>"
    )


# ------------------ Auth Routes ------------------

from flask import request, jsonify
from datetime import datetime
import random

@app.route('/eva-listen')
def eva_listen():
    query = request.args.get('query')
    if not query:
        return jsonify({"message": "Sorry, I didn’t catch that."})

    user_input = query.lower()

    def parse_command(text):
        commands = {
            "unread": {"action": "unread", "redirect": "/dashboard?filter=unread"},
            "read latest": {"action": "read_latest", "redirect": None},
            "summarize": {"action": "summarize", "redirect": None},
            "summary": {"action": "summarize", "redirect": None},
            "reply": {"action": "reply", "redirect": None},
            "respond": {"action": "reply", "redirect": None},
            "logout": {"action": "logout", "redirect": "/logout"},
            "log out": {"action": "logout", "redirect": "/logout"},
            "compose": {"action": "compose", "redirect": "/compose"},
            "write email": {"action": "compose", "redirect": "/compose"},
            "sent mail": {"action": "sent", "redirect": "/sent"},
            "sent": {"action": "sent", "redirect": "/sent"},
            "archive": {"action": "archived", "redirect": "/dashboard?filter=archive"},
            "inbox": {"action": "inbox", "redirect": "/dashboard"},
            "smart reply": {"action": "smart_reply", "redirect": None},
            "priority": {"action": "priority", "redirect": "/dashboard?filter=priority"},
            "reset password": {"action": "reset_password", "redirect": "/reset-password"},
            "settings": {"action": "settings", "redirect": "/settings"},
            "eva": {"action": "help", "redirect": None},
            "help": {"action": "help", "redirect": None},
        }

        for key in commands:
            if key in text:
                return commands[key]

        return {"action": "chat", "redirect": None}

    def get_greeting():
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning! "
        elif hour < 18:
            return "Good afternoon! "
        else:
            return "Good evening! "

    def generate_reply(text, action):
        if action["action"] == "chat":
            if any(greet in text for greet in ["hi", "hello", "hey", "yo", "hola", "what's up"]):
                return get_greeting() + "I'm EVA, your smart assistant. How can I help you today?"

            elif "how are you" in text or "how's it going" in text:
                return random.choice([
                    "I'm doing great! How can I assist you?",
                    "Feeling smart and focused today. Let's get things done.",
                    "I'm here and ready to help. What can I do for you?"
                ])

            elif "thank" in text or "thanks" in text:
                return random.choice([
                    "You're very welcome! 😊",
                    "Anytime! I'm always here to help.",
                    "Glad I could assist. Need anything else?"
                ])

            elif "what can you do" in text or "help" in text:
                return (
                    "I can read, summarize, reply, archive, and compose emails for you. "
                    "Try saying something like 'show unread emails' or 'compose a new email'."
                )

            elif "who are you" in text:
                return "I'm EVA — your Email Virtual Assistant. I help you stay on top of your inbox smartly."

            elif "bye" in text or "goodbye" in text:
                return "Goodbye! Have a productive day ahead."

            else:
                return "I'm listening. Try something like 'open inbox', 'summarize email', or 'compose an email'."

        replies = {
            "inbox": "Opening your inbox.",
            "unread": "Showing your unread emails.",
            "read_latest": "Reading your latest email now.",
            "summarize": "Summarizing recent emails.",
            "reply": "Ready to help you reply. What would you like to say?",
            "logout": "Logging you out now.",
            "compose": "Opening the compose email screen.",
            "sent": "Taking you to your sent mails.",
            "archived": "Opening the archive folder.",
            "smart_reply": "Opening smart reply options.",
            "priority": "Showing your priority emails.",
            "reset_password": "Opening password reset page.",
            "settings": "Opening your settings page.",
            "help": "I'm EVA. You can ask me to read emails, compose, summarize, or logout. Just say a command!"
        }

        return replies.get(action["action"], "Sorry, I didn't understand that.")

    action = parse_command(user_input)
    reply = generate_reply(user_input, action)

    return jsonify({
        "message": query,
        "reply": reply,
        "action": action["action"],
        "redirect": action["redirect"]
    })

#  Compose Email :

from models import SentEmail, Session
from datetime import datetime

@app.route("/download/<filename>")
@login_required
def download_attachment(filename):
    attachment_dir = os.path.join(app.root_path, "static", "attachments")
    return send_from_directory(attachment_dir, filename, as_attachment=True)

@app.route('/sent')
@login_required
def sent():
    session = Session()
    sent_emails = session.query(SentEmail).order_by(SentEmail.sent_at.desc()).all()
    return render_template("sent.html", sent_emails=sent_emails,active_page='sent')


UPLOAD_FOLDER = os.path.join('static', 'attachments')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    if request.method == 'POST':
        to_email = request.form['to']
        cc_email = request.form.get('cc')
        bcc_email = request.form.get('bcc')
        subject = request.form['subject']
        body = request.form['message']
        attachments = request.files.getlist('attachments')  # 🆕 Multiple files

        msg = MIMEMultipart()
        msg['From'] = EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        if cc_email:
            msg['Cc'] = cc_email
        if bcc_email:
            msg['Bcc'] = bcc_email

        msg.attach(MIMEText(body, 'plain'))

        attachment_filenames = []

        for attachment in attachments:
            if attachment and attachment.filename:
                filename = secure_filename(attachment.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                attachment.save(filepath)
                attachment_filenames.append(filename)

                part = MIMEBase('application', 'octet-stream')
                with open(filepath, 'rb') as f:
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                msg.attach(part)

        try:
            recipients = [to_email]
            if cc_email:
                recipients += cc_email.split(',')
            if bcc_email:
                recipients += bcc_email.split(',')

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL, APP_PASSWORD)
                server.sendmail(EMAIL, recipients, msg.as_string())

            # ✅ Save sent email to DB
            session = Session()
            sent_email = SentEmail(
                to=to_email,
                cc=cc_email,
                bcc=bcc_email,
                subject=subject,
                body=body,
                attachments=', '.join(attachment_filenames) if attachment_filenames else None,
                sent_at=datetime.utcnow()
            )
            session.add(sent_email)
            session.commit()

            flash("✅ Email sent successfully!", "success")
        except Exception as e:
            print(f"❌ Compose error: {e}")
            flash("❌ Failed to send email.", "danger")

        return redirect(url_for('dashboard'))

    return render_template('compose.html',active_page='compose')


from cryptography.fernet import Fernet
import os

fernet = Fernet(os.getenv("FERNET_KEY"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')
        hashed_pw = generate_password_hash(password)

        # Load shared Gmail credentials from .env
        shared_email = os.getenv("EMAIL")
        shared_password = os.getenv("APP_PASSWORD")
        encrypted_shared_pw = fernet.encrypt(shared_password.encode()).decode()

        session = Session()

        if session.query(User).filter_by(email=email).first():
            session.close()
            return "❌ Email already registered", 409

        user = User(
            email=email,
            password=hashed_pw,
            email_address=shared_email,
            imap_password_encrypted=encrypted_shared_pw,
            role=role,
            is_admin=(role.lower() == "admin")
        )

        session.add(user)
        session.commit()
        session.close()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember = 'remember' in request.form  # ✅ match HTML name

        session_db = Session()
        user = session_db.query(User).filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)  # ✅ remember works now
            session_db.close()
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid email or password"
            session_db.close()

    return render_template('login.html', error=error)



# from flask import request, redirect, url_for, render_template, make_response
# from flask_login import login_user
# from datetime import timedelta

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     saved_email = request.cookies.get('saved_email')  # ⬅️ fetch saved email from cookie

#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         remember = 'remember' in request.form  # ✅ match your HTML checkbox name

#         session_db = Session()
#         user = session_db.query(User).filter_by(email=email).first()

#         if user and user.check_password(password):
#             login_user(user, remember=remember)

#             # ✅ prepare response with cookie
#             resp = make_response(redirect(url_for('dashboard')))
#             if remember:
#                 resp.set_cookie(
#                     'saved_email',
#                     email,
#                     max_age=60*60*24*30,  # 30 days
#                     httponly=False,       # allow HTML to read it (safe since only email)
#                     secure=False          # set True if using HTTPS
#                 )
#             else:
#                 resp.delete_cookie('saved_email')

#             session_db.close()
#             return resp
#         else:
#             error = "Invalid email or password"
#             session_db.close()

#     # ⬅️ pass saved email into template
    # return render_template('login.html', error=error, saved_email=saved_email)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

# @app.route('/forgot-password', methods=['GET', 'POST'])
# def forgot_password():
#     if request.method == 'POST':
#         email = request.form['email']
#         session = Session()
#         user = session.query(User).filter_by(email=email).first()
#         session.close()
#         if user:
#             token = serializer.dumps(email, salt='email-reset')
#             reset_link = url_for('reset_password', token=token, _external=True)
#             send_reset_email(email, reset_link)
#             return "✅ Reset link sent to your email."
#         return "❌ Email not found."
#     return render_template('forgot_password.html')

# @app.route('/reset-password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     try:
#         email = serializer.loads(token, salt='email-reset', max_age=3600)
#     except SignatureExpired:
#         return "❌ The reset link has expired."
#     except BadSignature:
#         return "❌ Invalid or tampered link."

#     if request.method == 'POST':
#         new_password = request.form['password']
#         hashed_pw = generate_password_hash(new_password)
#         session = Session()
#         user = session.query(User).filter_by(email=email).first()
#         if user:
#             user.password = hashed_pw
#             session.commit()
#             session.close()
#             return "✅ Password reset successful. <a href='/login'>Login</a>."
#         session.close()
#         return "❌ User not found."
#     return render_template('reset_password.html', token=token)



@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    message = None
    if request.method == 'POST':
        email = request.form['email']
        session = Session()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        if user:
            token = serializer.dumps(email, salt='email-reset')
            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, reset_link)
            message = "✅ Reset link sent to your email."
        else:
            message = "❌ Email not found."
    return render_template('forgot_password.html', message=message)


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    message = None
    try:
        # Decode token
        email = serializer.loads(token, salt='email-reset', max_age=3600)
    except SignatureExpired:
        message = "❌ The reset link has expired."
        return render_template('reset_password.html', message=message, token=None)
    except BadSignature:
        message = "❌ Invalid or tampered link."
        return render_template('reset_password.html', message=message, token=None)

    if request.method == 'POST':
        new_password = request.form['password'].strip()
        if not new_password:
            message = "❌ Password cannot be empty."
            return render_template('reset_password.html', message=message, token=token)

        hashed_pw = generate_password_hash(new_password)
        session = Session()
        user = session.query(User).filter_by(email=email).first()
        if user:
            user.password = hashed_pw
            session.commit()
            session.close()
            message = "✅ Password reset successful. <a href='/login'>Login</a>."
        else:
            message = "❌ User not found."
            session.close()

    return render_template('reset_password.html', message=message, token=token)





def send_reset_email(to_email, link):
    msg = MIMEText(f"Click this link to reset your password:\n{link}")
    msg['Subject'] = 'Password Reset | Virtual Email Assistant'
    msg['From'] = EMAIL
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"❌ Email sending error: {e}")

@app.route('/refresh-emails')
@login_required
def refresh_emails():
    filter_type = request.args.get('filter', 'inbox')
    query = request.args.get('query', '').lower()
    session = Session()

    try:
        # ✅ Pull new emails from Gmail before loading from DB
        fetch_emails(EMAIL, APP_PASSWORD)

        # Now load from DB
        emails = session.query(EmailStatus).order_by(EmailStatus.timestamp.desc()).all()

        if filter_type == 'unread':
            emails = [e for e in emails if not e.read]
        elif filter_type == 'archived':
            emails = [e for e in emails if e.archived]
        elif filter_type == 'inbox':
            emails = [e for e in emails if not e.archived]

        if query:
            emails = [e for e in emails if query in e.subject.lower() or query in e.sender.lower()]

        return render_template('partials/email_list.html', emails=emails)
    except Exception as e:
        print(f"❌ Error during /refresh-emails: {e}")
        return "Internal Server Error", 500

from flask import render_template, redirect, url_for
from flask_login import current_user
from models import User, Session 

@app.route('/user_management')
@login_required
def user_management():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))

    session = Session()
    users = session.query(User).all()
    session.close()
    return render_template('user_management.html', users=users)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))

    if user_id == current_user.id:
        # Prevent deleting self
        return redirect(url_for('user_management'))

    session = Session()
    user = session.query(User).get(user_id)
    if user:
        session.delete(user)
        session.commit()
    session.close()
    return redirect(url_for('user_management'))



@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.query(User).get(int(user_id))
    if user:
        session.expunge(user)  # Detach object from session
        print(f"Loaded user {user.email} is_admin={user.is_admin}")
    else:
        print(f"No user found for id {user_id}")
    session.close()
    return user



# ------------------ Dashboard & Features ------------------


@app.route('/')
@app.route('/dashboard') 
@login_required
def dashboard():
    filter_type = request.args.get('filter', 'inbox')  # ✅ Default is inbox
    query = request.args.get('query', '').lower()
    session = Session()

    try:
        emails = fetch_emails(EMAIL, APP_PASSWORD)
    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        emails = []

    for e in emails:
        if not e['subject']:
            e['subject'] = "(No Subject)"

    existing_emails = {
        (e.subject, e.timestamp, e.sender)
        for e in session.query(EmailStatus.subject, EmailStatus.timestamp, EmailStatus.sender).all()
    }

    for e in emails:
        if not e['subject']:
            e['subject'] = "(No Subject)"

        ts = datetime.strptime(e['timestamp'], "%Y-%m-%dT%H:%M:%S")
        key = (e['subject'], ts, e['from'])

        if key not in existing_emails:
            category = categorize_email(e['subject'], e['summary'])
            priority = assign_priority(e['subject'], e['summary'])
            new_email = EmailStatus(
                subject=e['subject'],
                sender=e['from'],
                summary=e['summary'],
                timestamp=ts,
                classification=category.title(),
                read=False,
                archived=False,
                priority=priority
            )
            session.add(new_email)
            session.commit()

    # 📬 Filter logic
    emails_query = session.query(EmailStatus).filter_by(archived=False)
    if filter_type == 'archived':
        emails_query = session.query(EmailStatus).filter_by(archived=True)
    elif filter_type == 'unread':
        emails_query = emails_query.filter_by(read=False)
    elif filter_type == 'read':
        emails_query = emails_query.filter_by(read=True)

    emails = emails_query.order_by(EmailStatus.timestamp.desc()).all()

    # 🔍 Search logic
    if query:
        emails = [
            e for e in emails
            if query in e.sender.lower() or query in e.subject.lower() or query in e.classification.lower()
        ]

    # 💡 Smart reply generation
    for e in emails:
        if not e.smart_reply:
            if len(e.summary.split()) > 5 and e.classification.lower() != "spam":
                e.smart_reply = generate_smart_reply(f"{e.subject} {e.summary}")
            else:
                e.smart_reply = "(No smart reply)"

    session.commit()

    # 🟦 Active page logic
    if filter_type == 'unread':
        active_page = 'unread'
    elif filter_type == 'read':
        active_page = 'read'
    elif filter_type == 'archived':
        active_page = 'archived'
    else:
        active_page = 'inbox'

    # ⛔ DO NOT close session yet
    response = render_template(
    'dashboard.html',
    emails=emails,
    query=query,
    filter_mode=filter_type,
    active_page=active_page,
    current_user=current_user,
    role=getattr(current_user, 'role', 'user'),       # default 'user' if no role
    is_admin=getattr(current_user, 'is_admin', False) # default False if missing
)


    # ✅ Now safe to close
    session.expunge_all()
    session.close()

    return response


# Routes of commands

@app.route('/inbox')
@login_required
def inbox():
    return redirect(url_for('dashboard', filter='inbox'))

@app.route('/archived')
@login_required
def archived():
    return redirect(url_for('dashboard', filter='archived'))

@app.route('/read')
@login_required
def read():
    return redirect(url_for('dashboard', filter='read'))

@app.route('/unread')
@login_required
def unread():
    return redirect(url_for('dashboard', filter='unread'))



from flask import jsonify

@app.route('/delete_sent_email/<int:email_id>', methods=['DELETE'])
def delete_sent_email(email_id):
    session = Session()
    email = session.query(SentEmail).filter_by(id=email_id).first()
    if email:
        session.delete(email)
        session.commit()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Email not found"})

# from flask import jsonify
# from email_model import Session, EmailStatus  

# @app.route('/reminder_count')
# def reminder_count():
#     try:
#         session = Session()
#         count = session.query(EmailStatus).filter_by(reminder=True, read=False).count()
#         return jsonify({'count': count})
#     except Exception as e:
#         print("🔥 ERROR in /reminder_count:", e)
#         return jsonify({'count': 0, 'error': str(e)}), 500



@app.route('/reply', methods=['POST'])
@login_required
def reply():
    to_email = request.form['to']
    body = request.form['message']
    msg = MIMEText(body)
    msg['Subject'] = 'Reply from Assistant'
    msg['From'] = EMAIL
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"❌ Reply error: {e}")
    return redirect('/')

@app.route('/mark_read', methods=['POST'])
@login_required
def mark_read():
    subject = request.get_json().get('subject')
    session = Session()
    email = session.query(EmailStatus).filter_by(subject=subject).first()
    if email:
        email.read = True
        session.commit()
    session.close()
    return jsonify(success=True)

@app.route('/delete', methods=['POST'])
@login_required
def delete_email():
    subject = request.get_json().get('subject')
    session = Session()
    email = session.query(EmailStatus).filter_by(subject=subject).first()
    if email:
        session.delete(email)
        session.commit()
    session.close()
    return jsonify(success=True)

@app.route('/archive', methods=['POST'])
@login_required
def archive_email():
    email_id = request.form.get('email_id')
    session = Session()
    email = session.query(EmailStatus).get(email_id)
    if email:
        email.archived = True
        session.commit()
    session.close()
    return redirect(url_for('dashboard'))

@app.route('/unarchive', methods=['POST'])
@login_required
def unarchive_email():
    email_id = request.form.get('email_id')
    session = Session()
    email = session.query(EmailStatus).get(email_id)
    if email:
        email.archived = False
        session.commit()
    session.close()
    return redirect(url_for('dashboard', filter='archived'))


@app.route('/smart_reply', methods=['POST'])
@login_required
def smart_reply():
    context = request.get_json().get('context', '')
    if not context:
        return jsonify(reply="(No context)"), 400
    reply = generate_smart_reply(context)
    return jsonify(reply=reply)

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime


@app.route('/reminders')
@login_required
def reminders():
    session = Session()
    reminders = session.query(EmailStatus).filter_by(reminder=True).all()

    from datetime import datetime
    for r in reminders:
        print(f"🕒 Reminder: {r.timestamp}, Now: {datetime.now()}, Delta: {r.timestamp - datetime.now()}")

    return render_template('reminder.html', reminders=reminders, active_page='reminder', get_urgency_class=get_urgency_class)


from datetime import datetime

@app.route('/set-reminder/<int:email_id>', methods=['POST'])
@login_required
def set_reminder(email_id):
    session = Session()
    email = session.query(EmailStatus).filter_by(id=email_id).first()
    
    if email:
        reminder_time_str = request.form.get('reminder_time')  # e.g., "07/25/2025 03:30 PM"
        try:
            reminder_time = datetime.strptime(reminder_time_str, "%m/%d/%Y %I:%M %p")
            email.reminder = True
            email.timestamp = reminder_time  # ✅ Store it as datetime
            session.commit()
            return jsonify({'success': True})
        except Exception as e:
            print("❌ Time parsing error:", e)
            return jsonify({'success': False, 'error': 'Invalid time format'})
    
    return jsonify({'success': False})


@app.route('/toggle-reminder/<int:email_id>', methods=['POST'])
def toggle_reminder(email_id):
    data = request.get_json(silent=True)
    reminder_time = data.get('reminder_time') if data else None

    session = Session()
    email = session.query(EmailStatus).get(email_id)

    if email:
        if reminder_time:
            email.reminder = True
            email.reminder_time = reminder_time  # Save the time
        else:
            email.reminder = not email.reminder
            if not email.reminder:
                email.reminder_time = None
        session.commit()
        return jsonify({'success': True, 'reminder': email.reminder})
    return jsonify({'success': False}), 404


@app.route('/delete-reminder/<int:id>')
@login_required
def delete_reminder(id):
    session = Session()
    email = session.query(EmailStatus).filter_by(id=id).first()
    if email:
        email.reminder = False  # ✅ Correct column name
        session.commit()
    session.close()
    return redirect(url_for('reminders'))

from datetime import datetime, timedelta

from datetime import datetime, timedelta

def get_urgency_class(timestamp):
    now = datetime.now()
    if timestamp < now:
        return 'overdue'         # 🔴 Time has already passed
    elif timestamp <= now + timedelta(hours=6):
        return 'urgent'          # 🟠 Within the next 6 hours
    else:
        return 'normal'          # 🟢 Future reminders

from flask import jsonify
from grammar import improve_grammar

@app.route("/improve_grammar", methods=["POST"])
def grammar_route():
    data = request.get_json()
    text = data.get("text", "")
    improved = improve_grammar(text)
    return jsonify({"improved": improved})


# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)


