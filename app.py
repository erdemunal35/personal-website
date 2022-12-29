from flask import Flask, render_template
# import os

# project_root = os.path.dirname(__file__)
# template_path = os.path.join(project_root, 'web_code')
# app = Flask(__name__, template_folder=template_path, static_folder=template_path)

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000)
    # app.run()

# gunicorn --workers 1 --threads 1 --bind 0.0.0.0:7000 --reload app:app 