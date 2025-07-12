    # Map filter_type to active_page for sidebar highlighting
    if filter_type == 'unread':
        active_page = 'unread'
    elif filter_type == 'read':
        active_page = 'read'
    elif filter_type == 'archived':
        active_page = 'archived'
    else:
        active_page = 'inbox'

    return render_template('dashboard.html', emails=emails, query=query, filter_mode=filter_type, active_page=active_page,)