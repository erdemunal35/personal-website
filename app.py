import os
import secrets
import logging
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, send_from_directory, abort, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

app.config['UPLOAD_FOLDER'] = "files"
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

limiter = Limiter(key_func=get_remote_address, app=app, default_limits=[])


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
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
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
    return render_template('index.html', maps_api_key=maps_api_key)


@app.route('/contact', methods=['POST'])
def contact():
    if request.form.get('website', '').strip():
        logging.info("Contact form honeypot triggered — dropping submission")
        return jsonify({"ok": True})

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()
    logging.info("Contact form submission — name=%s email=%s", name, email)

    gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
    if gmail_password:
        try:
            body = f"Name: {name}\nEmail: {email}\n\n{message}"
            msg = MIMEText(body)
            msg['Subject'] = f"Portfolio contact from {name}"
            msg['From'] = 'erdem.unal96@gmail.com'
            msg['To'] = 'erdem.unal96@gmail.com'
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login('erdem.unal96@gmail.com', gmail_password)
                server.send_message(msg)
        except Exception as e:
            logging.error("Failed to send contact email: %s", e)

    return jsonify({"ok": True})


@app.route('/downloads/<filename>', methods=['GET'])
@limiter.limit("20 per minute")
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == "__main__":
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
