from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def hello():
    return render_template('index.html')

app.config['UPLOAD_FOLDER'] = "files"

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    # Returning file from appended path
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

# Debug/Development
# gunicorn --workers 1 --threads 1 --bind 0.0.0.0:7000 --reload app:app  