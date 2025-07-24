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
