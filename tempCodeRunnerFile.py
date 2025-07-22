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