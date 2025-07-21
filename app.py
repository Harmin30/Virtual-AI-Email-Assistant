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
from models import SentEmail, Session
from datetime import datetime
from flask import send_from_directory
# from eva_voice import speak, listen

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

@app.route('/eva-listen')
def eva_listen():
    query = listen()
    if query:
        speak(f"You said: {query}")
    return jsonify({"message": query or "Sorry, I didn’t catch that."})


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

# Enhance Text

# @app.route("/enhance-text", methods=["POST"])
# def enhance_text():
#     data = request.get_json()
#     text = data.get("text", "")

#     if not text:
#         return jsonify(success=False, error="No text provided.")


#     enhanced = text.capitalize().strip() + " 😊"

#     return jsonify(success=True, enhanced=enhanced)




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
    subject = request.get_json().get('subject')
    session = Session()
    email = session.query(EmailStatus).filter_by(subject=subject).first()
    if email:
        email.archived = True
        session.commit()
    session.close()
    return jsonify(success=True)

@app.route('/smart_reply', methods=['POST'])
@login_required
def smart_reply():
    context = request.get_json().get('context', '')
    if not context:
        return jsonify(reply="(No context)"), 400
    reply = generate_smart_reply(context)
    return jsonify(reply=reply)

import threading
from background_fetcher import background_fetch_emails





# Start background thread
fetch_thread = threading.Thread(target=background_fetch_emails, daemon=True)
fetch_thread.start()

# ------------------ Run App ------------------
if __name__ == '__main__':
    app.run(debug=True)
