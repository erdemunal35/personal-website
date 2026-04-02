import os
import secrets
import logging
from flask import Flask, render_template, send_from_directory, abort

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

app.config['UPLOAD_FOLDER'] = "files"


@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://code.iconify.design; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data: https:; "
        "frame-src https://www.google.com; "
        "connect-src 'self'"
    )
    response.headers['Permissions-Policy'] = (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=(), "
        "interest-cohort=(), accelerometer=(), gyroscope=(), magnetometer=()"
    )
    return response


@app.route('/')
def hello():
    maps_api_key = os.environ.get('MAPS_API_KEY', '')
    formspree_id = os.environ.get('FORMSPREE_ID', '')
    return render_template('index.html', maps_api_key=maps_api_key, formspree_id=formspree_id)


@app.route('/downloads/<filename>', methods=['GET'])
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
