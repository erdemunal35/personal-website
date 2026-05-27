import os
import re
import secrets
import logging
import smtplib
import hmac
import hashlib
import time
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


CAPTCHA_TTL = 30 * 60
CAPTCHA_MIN_AGE = 2
CAPTCHA_DIFFICULTY = 14

CYRILLIC_RE = re.compile(r'[Ѐ-ӿ]')
URL_RE = re.compile(r'https?://|www\.', re.IGNORECASE)
SPAM_KEYWORDS_RE = re.compile(
    r'\b(seo|backlink|crypto|casino|loan|viagra|bitcoin|telegram|whatsapp\s*\+?\d|порно|секс)\b',
    re.IGNORECASE,
)


def _captcha_secret():
    s = app.secret_key
    return s.encode() if isinstance(s, str) else s


def issue_captcha_token():
    ts = str(int(time.time()))
    rand = secrets.token_urlsafe(9)
    payload = f"{ts}.{rand}"
    sig = hmac.new(_captcha_secret(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{payload}.{sig}"


def verify_captcha(token, nonce):
    if not token or not nonce or len(nonce) > 32:
        return False, "missing"
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False, "malformed"
        ts_str, rand, sig = parts
        payload = f"{ts_str}.{rand}"
        expected = hmac.new(_captcha_secret(), payload.encode(), hashlib.sha256).hexdigest()[:32]
        if not hmac.compare_digest(sig, expected):
            return False, "bad-sig"
        age = int(time.time()) - int(ts_str)
        if age < CAPTCHA_MIN_AGE:
            return False, "too-fast"
        if age > CAPTCHA_TTL:
            return False, "expired"
        h = hashlib.sha256(f"{token}.{nonce}".encode()).digest()
        bits = int.from_bytes(h[:4], "big")
        if bits >> (32 - CAPTCHA_DIFFICULTY) != 0:
            return False, "bad-pow"
        return True, "ok"
    except (ValueError, TypeError):
        return False, "exception"


def looks_like_spam(name, email, message):
    blob = f"{name}\n{email}\n{message}"
    if CYRILLIC_RE.search(blob):
        return "cyrillic"
    url_hits = len(URL_RE.findall(message))
    if url_hits >= 2:
        return "too-many-urls"
    if SPAM_KEYWORDS_RE.search(blob):
        return "spam-keyword"
    if len(message) < 10 or len(message) > 5000:
        return "length"
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return "bad-email"
    return None


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
    return render_template(
        'index.html',
        maps_api_key=maps_api_key,
        captcha_token=issue_captcha_token(),
        captcha_difficulty=CAPTCHA_DIFFICULTY,
    )


@app.route('/contact', methods=['POST'])
@limiter.limit("5 per minute")
def contact():
    if request.form.get('website', '').strip():
        logging.info("Contact form honeypot triggered — dropping submission")
        return jsonify({"ok": True})

    ok, reason = verify_captcha(
        request.form.get('captcha_token', ''),
        request.form.get('captcha_nonce', ''),
    )
    if not ok:
        logging.info("Contact form CAPTCHA failed (%s) — dropping submission", reason)
        return jsonify({"ok": True})

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    message = request.form.get('message', '').strip()

    spam_reason = looks_like_spam(name, email, message)
    if spam_reason:
        logging.info("Contact form spam-filter dropped submission (%s) — email=%s", spam_reason, email)
        return jsonify({"ok": True})

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
