# Security Improvements — Medium Priority Backlog

These items were identified during a security audit (2026-03-30) and deferred for a later sprint.
Critical and High priority issues have already been fixed.

---

## 1. Update Outdated JavaScript Libraries

**File:** `static/js/`

| Library | Current | Status | Action |
|---------|---------|--------|--------|
| jQuery | 3.3.1 | Outdated (CVE-2020-11023, CVE-2020-11022) | Upgrade to 3.7.x |
| Bootstrap | ~4.x | Unconfirmed version | Verify and upgrade to 5.x |
| iconify-icon | 1.0.2 | Outdated | Upgrade to 2.x |

**Steps:**
- Download latest jQuery from https://jquery.com/download/
- Replace `static/js/jquery-3.3.1.min.js` with new file + update `index.html` reference
- Update Bootstrap if version is < 4.6.2

---

## 2. Upgrade Python Runtime from 3.7 (EOL)

**File:** `app.yaml`

Python 3.7 reached end-of-life on 2023-06-27 and no longer receives security patches.

**Action:** Change `runtime: python37` → `runtime: python312` in `app.yaml`.
> Note: Also update the Cloud Run build config / Dockerfile runtime base image to `python:3.12-slim`.

---

## 3. Add Subresource Integrity (SRI) to External CDN Scripts

**File:** `templates/index.html` line ~325

External scripts loaded without integrity verification are vulnerable if the CDN is compromised.

**Action:** Add `integrity` and `crossorigin` attributes to the iconify-icon script tag:
```html
<script src="https://code.iconify.design/iconify-icon/1.0.2/iconify-icon.min.js"
        integrity="sha384-<HASH>"
        crossorigin="anonymous"></script>
```
Generate the hash with:
```bash
curl -s https://code.iconify.design/iconify-icon/1.0.2/iconify-icon.min.js | openssl dgst -sha384 -binary | openssl base64 -A
```

---

## 4. Restrict Google Maps API Key in Google Cloud Console

**Even though the key is no longer in source code**, it is still embedded in the rendered HTML
(visible to end users via browser DevTools). Apply API-level restrictions:

1. Go to [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)
2. Select the Maps Embed API key
3. Under **Application restrictions** → set to **HTTP referrers**
4. Add: `https://your-domain.com/*` and `https://*.run.app/*`
5. Under **API restrictions** → restrict to **Maps Embed API** only
6. The previous key was exposed in git history before the history rewrite — **rotate it immediately** in GCP Console

---

## 5. Fix Contact Form (Currently Non-Functional)

**File:** `templates/index.html` line 274

The form uses `action="mailto:..."` with `method="post"` — this does not work in most browsers
and sends no data server-side.

**Options:**
- A) Implement a `/contact` Flask route that uses `smtplib` or a service like SendGrid/Mailgun
- B) Use Formspree (https://formspree.io) — drop-in form backend, no server-side code needed:
  ```html
  <form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
  ```
- C) Remove the form and replace with a direct mailto link

---

## 6. Google Fonts — Self-Host or Accept CDN Risk

**File:** `static/css/tooplate-style.css` line 8

Google Fonts is loaded via `@import url(...)` with no SRI. While Google Fonts CDN is reliable,
self-hosting eliminates the third-party dependency entirely:

```bash
# Use google-webfonts-helper to download and generate CSS
# https://gwfh.mranftl.com/fonts/maven-pro
```

---

## 7. Add Rate Limiting to `/downloads/` Endpoint

**File:** `app.py`

The CV download endpoint has no rate limiting. Install `flask-limiter`:
```bash
pip install flask-limiter
```
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/downloads/<filename>', methods=['GET'])
@limiter.limit("20 per minute")
def download(filename):
    ...
```

---

## 8. Session Cookie Security Configuration

**File:** `app.py`

Add the following to Flask config once session cookies are actually used:
```python
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

*Last updated: 2026-03-30 — Audit performed by Claude Code*
