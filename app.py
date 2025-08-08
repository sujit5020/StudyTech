from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import openai
import os
import json

from backend.quiz_generator import generate_quiz_from_text

from backend.summarizer import summarize_pdf

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains


# 🏠 Optional homepage route (not required)
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    try:
        data = request.get_json()
        mode = data.get("mode", "mcq")
        text = data.get("text", "")
        num_questions = int(data.get("num_questions", 5))  # Optional: allow frontend to choose

        if not text.strip():
            return jsonify({"error": "Please provide valid input text."}), 400
        if mode=='mcq':

            result = generate_quiz_from_text(text)


        print(json.dumps(result, indent=2))
        return jsonify({"questions": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    summary = summarize_pdf(filepath)
    return jsonify({"summary": summary})
    





if __name__ == "__main__":
    app.run(debug=True)

