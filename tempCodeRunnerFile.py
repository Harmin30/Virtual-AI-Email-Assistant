happy_tt = HappyTextToText("T5", "vennify/t5-base-grammar-correction")

@app.route('/fix_grammar', methods=['POST'])
def fix_grammar():
    data = request.get_json()
    raw_text = data.get("text", "")

    if not raw_text.strip():
        return jsonify({"corrected": ""})

    result = happy_tt.generate_text(f"grammar: {raw_text}")
    return jsonify({"corrected": result.text})