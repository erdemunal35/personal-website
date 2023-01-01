from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for

# project_root = os.path.dirname(__file__)
# template_path = os.path.join(project_root, 'web_code')
# app = Flask(__name__, template_folder=template_path, static_folder=template_path)

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
    app.run(host="0.0.0.0", port=7000)
    # app.run()

# gunicorn --workers 1 --threads 1 --bind 0.0.0.0:7000 --reload app:app  