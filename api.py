"""
Community Builders Network - Sierra Leone
API endpoint handlers.

Each function accepts (handler, data) where:
  - handler : the BaseHTTPRequestHandler instance (for auth headers, cookies)
  - data    : dict parsed from JSON body (POST) or query params (GET)

They return (status_code, json_dict).
"""

from datetime import datetime, timedelta

import db
from utils import clean, is_email, require, new_session_token, verify_password


# ==================================================================
# PUBLIC endpoints — no auth
# ==================================================================

# ---------- Contact form ----------
def api_contact(handler, data):
    missing = require(data, ["full_name", "email", "message"])
    if missing:
        return 400, {"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}
    if not is_email(data.get("email", "")):
        return 400, {"ok": False, "error": "Invalid email address."}

    db.execute(
        """INSERT INTO contact_submissions
             (full_name, email, phone, subject, message)
           VALUES (%s, %s, %s, %s, %s)""",
        (
            clean(data.get("full_name"), 150),
            clean(data.get("email"), 150),
            clean(data.get("phone"), 50),
            clean(data.get("subject"), 200),
            clean(data.get("message"), 5000),
        ),
    )
    return 200, {"ok": True, "message": "Thank you! Your message has been received. We will reply within 3 working days."}


# ---------- Volunteer application ----------
def api_volunteer(handler, data):
    missing = require(data, ["first_name", "last_name", "email"])
    if missing:
        return 400, {"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}
    if not is_email(data.get("email", "")):
        return 400, {"ok": False, "error": "Invalid email address."}

    db.execute(
        """INSERT INTO volunteer_applications
             (first_name, last_name, email, phone, role, availability, message)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            clean(data.get("first_name"), 100),
            clean(data.get("last_name"), 100),
            clean(data.get("email"), 150),
            clean(data.get("phone"), 50),
            clean(data.get("role"), 150),
            clean(data.get("availability"), 150),
            clean(data.get("message"), 5000),
        ),
    )
    return 200, {"ok": True, "message": "Thank you! Your volunteer application has been received. Our team will be in touch within 3 working days."}


# ---------- Partnership enquiry ----------
def api_partner(handler, data):
    missing = require(data, ["organisation", "contact_name", "contact_email"])
    if missing:
        return 400, {"ok": False, "error": f"Missing required fields: {', '.join(missing)}"}
    if not is_email(data.get("contact_email", "")):
        return 400, {"ok": False, "error": "Invalid contact email address."}

    db.execute(
        """INSERT INTO partner_enquiries
             (organisation, org_type, contact_name, contact_email,
              interest_area, budget_range, message)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            clean(data.get("organisation"), 200),
            clean(data.get("org_type"), 100),
            clean(data.get("contact_name"), 150),
            clean(data.get("contact_email"), 150),
            clean(data.get("interest_area"), 100),
            clean(data.get("budget_range"), 100),
            clean(data.get("message"), 5000),
        ),
    )
    return 200, {"ok": True, "message": "Thank you! Your partnership enquiry has been received."}


# ---------- Newsletter subscribe ----------
def api_newsletter(handler, data):
    email = clean(data.get("email"), 150).lower()
    if not is_email(email):
        return 400, {"ok": False, "error": "Please enter a valid email address."}

    # UPSERT (re-activate if already exists)
    db.execute(
        """INSERT INTO newsletter_subscribers (email, active)
           VALUES (%s, 1)
           ON DUPLICATE KEY UPDATE active = 1""",
        (email,),
    )
    return 200, {"ok": True, "message": "You're subscribed! Watch your inbox for the next CBN update."}


# ---------- Content: projects ----------
def api_projects(handler, data):
    status = clean(data.get("status", "")).lower()
    category = clean(data.get("category", "")).lower()
    where, params = [], []
    if status in ("current", "past"):
        where.append("status = %s"); params.append(status)
    if category:
        where.append("category = %s"); params.append(category)
    sql = "SELECT id, title, slug, category, status, location, start_year, end_year, summary, image_url, funded_pct, featured FROM projects"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY featured DESC, id DESC"
    rows = db.query(sql, tuple(params))
    return 200, {"ok": True, "count": len(rows), "items": rows}


# ---------- Content: blog ----------
def api_blog(handler, data):
    category = clean(data.get("category", "")).lower()
    where, params = [], []
    if category and category != "all":
        where.append("category = %s"); params.append(category)
    sql = ("SELECT id, title, slug, category, author, excerpt, image_url, "
           "read_minutes, published_at, featured FROM blog_posts")
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY featured DESC, published_at DESC"
    rows = db.query(sql, tuple(params))
    # Serialise dates
    for r in rows:
        if r.get("published_at"):
            r["published_at"] = r["published_at"].isoformat()
    return 200, {"ok": True, "count": len(rows), "items": rows}


# ---------- Content: events ----------
def api_events(handler, data):
    rows = db.query(
        "SELECT id, title, location, event_date, event_time, description, cta_label, cta_url "
        "FROM events WHERE event_date >= CURDATE() ORDER BY event_date ASC"
    )
    for r in rows:
        if r.get("event_date"):
            r["event_date"] = r["event_date"].isoformat()
    return 200, {"ok": True, "count": len(rows), "items": rows}


# ---------- Content: success stories ----------
def api_stories(handler, data):
    rows = db.query(
        "SELECT id, name, role, quote, image_url FROM success_stories ORDER BY id DESC"
    )
    return 200, {"ok": True, "count": len(rows), "items": rows}


# ==================================================================
# ADMIN endpoints
# ==================================================================

def _require_admin(handler):
    """Returns admin_id if session is valid, else None."""
    token = handler.headers.get("X-Admin-Token")
    if not token:
        # Also allow cookie
        cookie = handler.headers.get("Cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith("cbn_admin="):
                token = part[len("cbn_admin="):]
                break
    if not token:
        return None
    row = db.query(
        "SELECT admin_id, expires_at FROM admin_sessions WHERE token = %s",
        (token,), one=True,
    )
    if not row:
        return None
    if row["expires_at"] < datetime.now():
        return None
    return row["admin_id"]


def api_admin_login(handler, data):
    username = clean(data.get("username"), 80)
    password = data.get("password") or ""
    if not username or not password:
        return 400, {"ok": False, "error": "Username and password are required."}

    row = db.query(
        "SELECT id, password_hash, full_name FROM admin_users WHERE username = %s",
        (username,), one=True,
    )
    if not row or not verify_password(password, row["password_hash"]):
        return 401, {"ok": False, "error": "Invalid credentials."}

    from config import SESSION_LIFETIME_HOURS
    token = new_session_token()
    expires = datetime.now() + timedelta(hours=SESSION_LIFETIME_HOURS)
    db.execute(
        "INSERT INTO admin_sessions (admin_id, token, expires_at) VALUES (%s, %s, %s)",
        (row["id"], token, expires),
    )
    # Set cookie on the response
    handler._set_cookie = f"cbn_admin={token}; Path=/; HttpOnly; SameSite=Lax; Max-Age={SESSION_LIFETIME_HOURS*3600}"
    return 200, {"ok": True, "token": token, "user": {"id": row["id"], "name": row["full_name"]}}


def api_admin_logout(handler, data):
    token = handler.headers.get("X-Admin-Token")
    if not token:
        cookie = handler.headers.get("Cookie", "")
        for part in cookie.split(";"):
            part = part.strip()
            if part.startswith("cbn_admin="):
                token = part[len("cbn_admin="):]
                break
    if token:
        db.execute("DELETE FROM admin_sessions WHERE token = %s", (token,))
    handler._set_cookie = "cbn_admin=; Path=/; Max-Age=0"
    return 200, {"ok": True}


def api_admin_me(handler, data):
    admin_id = _require_admin(handler)
    if not admin_id:
        return 401, {"ok": False, "error": "Not authenticated."}
    row = db.query("SELECT id, username, full_name FROM admin_users WHERE id = %s",
                   (admin_id,), one=True)
    return 200, {"ok": True, "user": row}


def api_admin_dashboard(handler, data):
    if not _require_admin(handler):
        return 401, {"ok": False, "error": "Not authenticated."}
    counts = {
        "contact":    db.query("SELECT COUNT(*) c FROM contact_submissions",     one=True)["c"],
        "volunteer":  db.query("SELECT COUNT(*) c FROM volunteer_applications",  one=True)["c"],
        "partner":    db.query("SELECT COUNT(*) c FROM partner_enquiries",       one=True)["c"],
        "newsletter": db.query("SELECT COUNT(*) c FROM newsletter_subscribers WHERE active=1", one=True)["c"],
    }
    new_counts = {
        "contact":   db.query("SELECT COUNT(*) c FROM contact_submissions WHERE status='new'",     one=True)["c"],
        "volunteer": db.query("SELECT COUNT(*) c FROM volunteer_applications WHERE status='new'",  one=True)["c"],
        "partner":   db.query("SELECT COUNT(*) c FROM partner_enquiries WHERE status='new'",       one=True)["c"],
    }
    return 200, {"ok": True, "totals": counts, "new": new_counts}


def _list_table(handler, table, columns):
    if not _require_admin(handler):
        return 401, {"ok": False, "error": "Not authenticated."}
    rows = db.query(
        f"SELECT {columns} FROM {table} ORDER BY created_at DESC LIMIT 200"
    )
    for r in rows:
        for k, v in list(r.items()):
            if isinstance(v, datetime):
                r[k] = v.isoformat(sep=" ", timespec="minutes")
    return 200, {"ok": True, "count": len(rows), "items": rows}


def api_admin_contact(handler, data):
    return _list_table(handler, "contact_submissions",
        "id, full_name, email, phone, subject, message, status, created_at")

def api_admin_volunteer(handler, data):
    return _list_table(handler, "volunteer_applications",
        "id, first_name, last_name, email, phone, role, availability, message, status, created_at")

def api_admin_partner(handler, data):
    return _list_table(handler, "partner_enquiries",
        "id, organisation, org_type, contact_name, contact_email, interest_area, budget_range, message, status, created_at")

def api_admin_newsletter(handler, data):
    return _list_table(handler, "newsletter_subscribers",
        "id, email, active, created_at")


# ==================================================================
# ROUTE MAP
# ==================================================================
POST_ROUTES = {
    "/api/contact":         api_contact,
    "/api/volunteer":       api_volunteer,
    "/api/partner":         api_partner,
    "/api/newsletter":      api_newsletter,
    "/api/admin/login":     api_admin_login,
    "/api/admin/logout":    api_admin_logout,
}

GET_ROUTES = {
    "/api/projects":            api_projects,
    "/api/blog":                api_blog,
    "/api/events":              api_events,
    "/api/stories":             api_stories,
    "/api/admin/me":            api_admin_me,
    "/api/admin/dashboard":     api_admin_dashboard,
    "/api/admin/contact":       api_admin_contact,
    "/api/admin/volunteer":     api_admin_volunteer,
    "/api/admin/partner":       api_admin_partner,
    "/api/admin/newsletter":    api_admin_newsletter,
}
