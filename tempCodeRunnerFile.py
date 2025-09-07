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