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


from flask import send_from_directory
# from eva_voice import speak, listen

import threading
import time
from datetime import datetime
# from email_model import get_due_reminders, mark_reminder_sent
# from flask import jsonify

import dateparser

# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate

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
# from happytransformer import HappyTextToText


# ------------------ Load Configuration ------------------
load_dotenv()
EMAIL = os.getenv('EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
SECRET_KEY = os.getenv('SECRET_KEY')


# ------------------ Flask App Setup ------------------
app = Flask(__name__)
app.secret_key = SECRET_KEY

# ✅ Add this config line before initializing SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Now initialize db
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)

serializer = URLSafeTimedSerializer(app.secret_key)


# ------------------ Login Setup ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------ AI Setup ------------------
model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-small")
tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-small")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")



# def init_reminders_table():
#     conn = get_db_connection()
#     cursor = conn.cursor()
    
#     # Create the table if it doesn't exist
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS reminders (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             subject TEXT NOT NULL,
#             reminder_time TEXT NOT NULL
#         )
#     """)
    
#     # Optional: remove 'full_datetime' if it exists (cleanup if you were testing earlier)
#     try:
#         cursor.execute("PRAGMA table_info(reminders)")
#         columns = [col[1] for col in cursor.fetchall()]
#         if 'full_datetime' in columns:
#             # Backup old data
#             cursor.execute("ALTER TABLE reminders RENAME TO reminders_old")
#             cursor.execute("""
#                 CREATE TABLE reminders (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     subject TEXT NOT NULL,
#                     reminder_time TEXT NOT NULL
#                 )
#             """)
#             cursor.execute("""
#                 INSERT INTO reminders (id, subject, reminder_time)
#                 SELECT id, subject, reminder_time FROM reminders_old
#             """)
#             cursor.execute("DROP TABLE reminders_old")
#     except Exception as e:
#         print("Error during full_datetime cleanup:", e)

#     conn.commit()
#     conn.close()


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

@login_manager.user_loader
def load_user(user_id):
    session = Session()
    user = session.get(User, int(user_id))
    session.close()
    return user

# ------------------ Auth Routes ------------------
 
# EVA Voice : 

# @app.route('/eva-listen')
# def eva_listen():
#     query = listen()
#     if query:
#         speak(f"You said: {query}")
#     return jsonify({"message": query or "Sorry, I didn’t catch that."})

# @app.route('/eva-listen')
# def eva_listen():
#     import random
#     from datetime import datetime

#     query = listen()
#     if not query:
#         speak("Sorry, I didn’t catch that.")
#         return jsonify({"message": "Sorry, I didn’t catch that."})

#     user_input = query.lower()

#     # 🎯 EVA Command Parser
#     def parse_command(text):
#         if "unread" in text:
#             return {"action": "unread"}
#         elif "read" in text and "latest" in text:
#             return {"action": "read_latest"}
#         elif "summarize" in text or "summary" in text:
#             return {"action": "summarize"}
#         elif "reply" in text or "respond" in text:
#             return {"action": "reply"}
#         elif "logout" in text or "log out" in text:
#             return {"action": "logout"}
#         elif "compose" in text or "write email" in text:
#             return {"action": "compose"}
#         elif "sent mail" in text or "sent" in text:
#             return {"action": "sent"}
#         elif "archive" in text:
#             return {"action": "archive"}
#         elif "inbox" in text:
#             return {"action": "inbox"}
#         elif "smart reply" in text:
#             return {"action": "smart_reply"}
#         elif "priority" in text:
#             return {"action": "priority"}
#         elif "reset password" in text:
#             return {"action": "reset_password"}
#         elif "settings" in text:
#             return {"action": "settings"}
#         elif "eva" in text or "help" in text:
#             return {"action": "help"}
#         else:
#             return {"action": "chat"}

#     # 💬 EVA Replies
#     def generate_reply(text, action):
#         if action["action"] == "chat":
#             if "hi" in text or "hello" in text:
#                 return get_greeting() + " I'm EVA, your smart assistant. 😊"
#             elif "how are you" in text:
#                 return random.choice([
#                     "I'm doing great! How can I assist you?",
#                     "Always ready to help you!",
#                     "Feeling smart and focused today. 😎"
#                 ])
#             elif "thank" in text:
#                 return "You're very welcome! 💙"
#             elif "what can you do" in text:
#                 return (
#                     "I can read, summarize, reply, archive emails, and guide you with voice commands. "
#                     "Try saying 'show unread emails' or 'compose a new email'."
#                 )
#             else:
#                 return "I'm listening. Try something like 'open inbox' or 'show sent emails'."

#         # 🔁 Route-specific reply
#         return {
#             "inbox": "Opening your inbox.",
#             "unread": "Showing your unread emails.",
#             "read_latest": "Reading your latest email now.",
#             "summarize": "Summarizing recent emails.",
#             "reply": "Ready to help you reply. What would you like to say?",
#             "logout": "Logging you out now.",
#             "compose": "Opening the compose email screen.",
#             "sent": "Taking you to your sent mails.",
#             "archive": "Opening the archive folder.",
#             "smart_reply": "Opening smart reply options.",
#             "priority": "Showing your priority emails.",
#             "reset_password": "Opening password reset page.",
#             "settings": "Opening your settings page.",
#             "help": "I'm EVA. You can ask me to read emails, compose, summarize, or logout. Just say a command!"
#         }.get(action["action"], "Sorry, I didn’t understand that.")

#     # ⏰ Greeting by time
#     def get_greeting():
#         hour = datetime.now().hour
#         if hour < 12:
#             return "Good morning! ☀️"
#         elif hour < 18:
#             return "Good afternoon! 🌤️"
#         else:
#             return "Good evening! 🌙"

#     action = parse_command(user_input)
#     reply = generate_reply(user_input, action)
#     speak(reply)

#     return jsonify({
#         "message": query,
#         "reply": reply,
#         "action": action["action"]
#     })


#  =============================

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



# @app.route('/dashboard')
# def dashboard_redirect():
#     return redirect(url_for('dashboard'))



# Load model only once
# happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")

# @app.route('/fix_grammar', methods=['POST'])
# def fix_grammar():
#     data = request.get_json()
#     raw_text = data.get("text", "")

#     if not raw_text.strip():
#         return jsonify({"corrected": ""})

#     result = happy_tt.generate_text(f"grammar: {raw_text}")
#     return jsonify({"corrected": result.text})


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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')
        hashed_pw = generate_password_hash(password)
        session = Session()
        if session.query(User).filter_by(email=email).first():
            session.close()
            return "❌ Email already registered", 409
        user = User(email=email, password=hashed_pw, role=role)
        session.add(user)
        session.commit()
        session.close()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session = Session()
        user = session.query(User).filter_by(email=request.form['email']).first()
        session.close()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect('/')
        return "❌ Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        session = Session()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        if user:
            token = serializer.dumps(email, salt='email-reset')
            reset_link = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, reset_link)
            return "✅ Reset link sent to your email."
        return "❌ Email not found."
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='email-reset', max_age=3600)
    except SignatureExpired:
        return "❌ The reset link has expired."
    except BadSignature:
        return "❌ Invalid or tampered link."

    if request.method == 'POST':
        new_password = request.form['password']
        hashed_pw = generate_password_hash(new_password)
        session = Session()
        user = session.query(User).filter_by(email=email).first()
        if user:
            user.password = hashed_pw
            session.commit()
            session.close()
            return "✅ Password reset successful. <a href='/login'>Login</a>."
        session.close()
        return "❌ User not found."
    return render_template('reset_password.html', token=token)

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
        active_page=active_page
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




# View all reminders
# @app.route('/reminders')
# def reminders():
#     conn = get_db_connection()
#     reminders = conn.execute("SELECT * FROM reminders ORDER BY full_datetime ASC").fetchall()
#     conn.close()
#     return render_template('reminder.html', reminders=reminders)



# @app.route('/set-reminder', methods=['POST'])
# def set_reminder():
#     subject = request.form.get('subject')
#     reminder_time = request.form.get('reminder_time')

#     if not subject or not reminder_time:
#         return "Missing subject or reminder_time", 400

#     conn = get_db_connection()
#     conn.execute(
#         "INSERT INTO reminders (subject, reminder_time) VALUES (?, ?)",
#         (subject, reminder_time)
#     )
#     conn.commit()
#     conn.close()

#     return jsonify({'status': 'Reminder set successfully'}), 200


# # Delete a reminder
# @app.route('/delete_reminder/<int:id>')
# def delete_reminder(id):
#     try:
#         conn = get_db_connection()
#         conn.execute("DELETE FROM reminders WHERE id = ?", (id,))
#         conn.commit()
#         flash('Reminder deleted successfully.', 'success')
#     except Exception as e:
#         flash(f'Error deleting reminder: {str(e)}', 'error')
#     finally:
#         conn.close()
#     return redirect('/reminders')

# # API: Get due reminders
# @app.route('/api/due-reminders')
# def get_due_reminders():
#     conn = get_db_connection()
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     rows = conn.execute("""
#         SELECT id, subject, reminder_time FROM reminders
#         WHERE reminder_time <= ?
#     """, (now,)).fetchall()
#     conn.close()
#     reminders = [{'id': row['id'], 'subject': row['subject'], 'reminder_time': row['reminder_time']} for row in rows]
#     return jsonify(reminders)


# # Background checker to notify due reminders (optional console log)
# def reminder_checker():
#     while True:
#         try:
#             conn = get_db_connection()
#             now = datetime.now()
#             due_reminders = conn.execute("""
#                 SELECT id, subject FROM reminders
#                 WHERE full_datetime <= ?
#             """, (now,)).fetchall()

#             for reminder in due_reminders:
#                 print(f"🔔 Reminder: {reminder['subject']}")
#                 # You can also send an in-app alert/email/etc.

#             conn.close()
#         except Exception as e:
#             print("Background reminder check error:", e)

#         time.sleep(60)  # Check every 60 seconds

# # Start background thread
# reminder_thread = threading.Thread(target=reminder_checker, daemon=True)
# reminder_thread.start()

# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)


