# Community Builders Network — Sierra Leone

Full-stack website for **Community Builders Network - Sierra Leone**, an NGO.
Built with:

| Layer     | Technology                                       |
|-----------|--------------------------------------------------|
| Frontend  | Pure HTML5, CSS3, vanilla JavaScript (no framework) |
| Backend   | Pure Python 3 (`http.server`, no framework)      |
| Database  | MySQL 8+ (`mysql-connector-python` driver only)  |

---

## 📁 Project structure

```
cbn-sierra-leone/
├── index.html            # Home
├── about.html            # About Us
├── projects.html         # Projects (Current / Past / Impact Stories)
├── get-involved.html     # Volunteer / Partner with Us + forms
├── news.html             # Blog / Events / Success Stories / Newsletter
├── contact.html          # Contact form
├── admin.html            # Admin dashboard (protected)
├── admin-login.html      # Admin login screen
├── styles.css            # Shared stylesheet (all pages + admin)
├── script.js             # Shared frontend JS (navbar, forms, animations)
│
├── backend/
│   ├── server.py         # Main HTTP server — python server.py
│   ├── api.py            # All /api/* endpoint handlers
│   ├── db.py             # MySQL connection pool + query helpers
│   ├── config.py         # Config (reads from env vars)
│   └── utils.py          # Password hashing, validators, tokens
│
├── database/
│   ├── schema.sql        # CREATE TABLE statements
│   └── seed.sql          # Sample content (projects, blog, events, stories)
│
├── requirements.txt      # Python dependencies (only mysql-connector-python)
└── README.md
```

---

## 🚀 Quick start (local development)

### 1. Prerequisites

- **Python 3.9+**
- **MySQL 8.0+** (or MariaDB 10.5+) running locally
- `pip` for installing the MySQL driver

### 2. Clone / download this project

```bash
git clone <your-repo-url> cbn-sierra-leone
cd cbn-sierra-leone
```

### 3. Set up the database

```bash
# Create the database + tables
mysql -u root -p < database/schema.sql

# (Optional) Load sample projects, blog posts, events, stories
mysql -u root -p cbn_sierra_leone < database/seed.sql
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the DB connection

Either edit `backend/config.py` directly, or export environment variables:

```bash
export DB_HOST=127.0.0.1
export DB_USER=root
export DB_PASSWORD=your_mysql_password
export DB_NAME=cbn_sierra_leone

# Optional — change the default admin password (created on first run)
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD='choose-a-strong-password'
```

### 6. Run the server

```bash
cd backend
python server.py
```

You should see:

```
Community Builders Network — starting server
  Static root : /.../cbn-sierra-leone
  Database    : 127.0.0.1:3306/cbn_sierra_leone
  Listening   : http://0.0.0.0:8000
  Admin panel : http://0.0.0.0:8000/admin
```

Open **<http://localhost:8000>** in your browser 🎉

---

## 🔐 Admin panel

- URL: <http://localhost:8000/admin>
- Default credentials (created automatically on first run):
  - Username: `admin`
  - Password: `admin123`  ← **change immediately via `ADMIN_PASSWORD` env var**

The dashboard shows all submissions from:

- Contact form
- Volunteer applications
- Partnership enquiries
- Newsletter subscribers

Sessions are stored in the `admin_sessions` table (12h lifetime by default) and
tracked via an `HttpOnly` cookie.

---

## 🌐 API endpoints

All endpoints return JSON. Public endpoints are unauthenticated; admin
endpoints require a valid session cookie or `X-Admin-Token` header.

### Public

| Method | Path                | Purpose                                  |
|--------|---------------------|------------------------------------------|
| POST   | `/api/contact`      | Contact form submission                  |
| POST   | `/api/volunteer`    | Volunteer application                    |
| POST   | `/api/partner`      | Partnership enquiry                      |
| POST   | `/api/newsletter`   | Newsletter subscribe                     |
| GET    | `/api/projects`     | List projects (`?status=current&category=education`) |
| GET    | `/api/blog`         | List blog posts (`?category=field`)      |
| GET    | `/api/events`       | Upcoming events                          |
| GET    | `/api/stories`      | Success stories                          |

### Admin

| Method | Path                       | Purpose                          |
|--------|----------------------------|----------------------------------|
| POST   | `/api/admin/login`         | Login (returns session cookie)   |
| POST   | `/api/admin/logout`        | Logout                           |
| GET    | `/api/admin/me`            | Current admin user               |
| GET    | `/api/admin/dashboard`     | Counts + new items               |
| GET    | `/api/admin/contact`       | List contact submissions         |
| GET    | `/api/admin/volunteer`     | List volunteer applications      |
| GET    | `/api/admin/partner`       | List partnership enquiries       |
| GET    | `/api/admin/newsletter`    | List newsletter subscribers      |

### Example (curl)

```bash
# Public — submit a contact message
curl -X POST http://localhost:8000/api/contact \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","email":"jane@example.com","message":"Hello!"}'

# Admin — log in and list submissions
curl -c cookies.txt -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
curl -b cookies.txt http://localhost:8000/api/admin/contact
```

---

## 📦 Deployment

### Option A — Simple VPS (Ubuntu/Debian)

```bash
# On the server
sudo apt update
sudo apt install -y python3 python3-pip mysql-server nginx

# Set up MySQL
sudo mysql_secure_installation
sudo mysql < database/schema.sql
sudo mysql cbn_sierra_leone < database/seed.sql   # optional

# Install Python driver
sudo pip3 install -r requirements.txt

# Create a systemd service
sudo tee /etc/systemd/system/cbn.service > /dev/null <<'EOF'
[Unit]
Description=CBN Sierra Leone website
After=network.target mysql.service

[Service]
User=www-data
WorkingDirectory=/var/www/cbn-sierra-leone/backend
Environment="DB_HOST=127.0.0.1"
Environment="DB_USER=cbn_user"
Environment="DB_PASSWORD=CHANGE_ME"
Environment="DB_NAME=cbn_sierra_leone"
Environment="ADMIN_PASSWORD=CHANGE_ME"
Environment="CBN_PORT=8000"
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now cbn
sudo systemctl status cbn
```

### Reverse proxy with Nginx + HTTPS

```nginx
server {
    listen 80;
    server_name cbn-sl.org www.cbn-sl.org;

    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

Then run:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d cbn-sl.org -d www.cbn-sl.org
```

### Option B — Docker (optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV CBN_PORT=8000 CBN_HOST=0.0.0.0
EXPOSE 8000
WORKDIR /app/backend
CMD ["python", "server.py"]
```

Then run alongside a MySQL container using `docker-compose`.

---

## 🔒 Security notes for production

1. **Change the default admin password** immediately (via `ADMIN_PASSWORD` env var).
2. Use a dedicated MySQL user with only the privileges it needs
   (`GRANT SELECT, INSERT, UPDATE, DELETE ON cbn_sierra_leone.*`).
3. Always deploy behind HTTPS (see the Nginx + Certbot example above).
4. Set `CBN_DEBUG=0` (default) so error tracebacks are not returned to clients.
5. Consider a WAF or rate-limiter (e.g. Nginx `limit_req`) in front of `/api/*`.
6. Regularly back up the `cbn_sierra_leone` database.

---

## 🛠 Troubleshooting

- **`ModuleNotFoundError: No module named 'mysql'`** →
  `pip install -r requirements.txt`
- **`Access denied for user …`** →
  double-check `DB_USER` / `DB_PASSWORD` env vars.
- **Nothing happens when I submit a form** →
  open the browser DevTools → *Network* tab; check the response from
  `/api/contact` (or similar). A 500 usually means the DB isn't reachable.
- **Admin login just refreshes the page** →
  the default password may already have been changed. Log in to MySQL and
  reset it manually, or drop the row from `admin_users` and restart the
  server to re-bootstrap.

---

## 📄 License

© Community Builders Network - Sierra Leone. All rights reserved.
