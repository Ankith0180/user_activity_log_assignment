# User Activity Log API

## Setup Instructions

```bash
git clone <repo_url>
cd activitylog_project
python -m venv venv
source venv/bin/activate

1. **Install dependencies**
    pip install -r requirements.txt
2. **Run migrations**
    python manage.py migrate
3. **Create superuser (optional)**
    python manage.py createsuperuser
4.**Run development server**
    python manage.py runserver
```

## Sample API Calls (Using curl)

### POST a new log
```bash
curl -X POST -H "Authorization: Token <token>" \
    -H "Content-Type: application/json" \
    -d '{"action": "LOGIN", "metadata": {"device": "mobile"}}' \
    http://127.0.0.1:8000/logs/
```

### GET all logs
```bash
curl -X GET -H "Authorization: Token <token>" \
    http://127.0.0.1:8000/logs/1/
```

### PATCH log status
```bash
curl -X PATCH -H "Authorization: Token <token>" \
    -H "Content-Type: application/json" \
    -d '{"status": "DONE"}' \
    http://127.0.0.1:8000/logs/1/status/
```

## Requirements
- Django
- Django REST Framework
- Redis
- psycopg2


# 🧾 User Activity Log API Documentation

Base URL:  
```
http://<your-domain>/logs/
```

---

## 🔹 1. Create User Activity Log 

**Endpoint:**  
`POST /logs/`

**Description:**  
Create a new activity log for the authenticated user.

**Authentication:**  
Required (Token or Session)

**Request Body (JSON):**
```json
{
  "action": "UPLOAD_FILE",
  "metadata": {
    "file_name": "test.pdf"
  }
}
```

**Response:**  
`201 Created`
```json
{
  "id": 1,
  "user": 1,
  "action": "UPLOAD_FILE",
  "metadata": {
    "file_name": "test.pdf"
  },
  "status": "PENDING",
  "timestamp": "2025-06-13T13:05:34.000Z"
}
```

---

## 🔹 2. List User Activity Logs

**Endpoint:**  
`GET /logs/<user_id>/`

**Description:**  
Retrieve all activity logs for a given user ID. Supports filtering and caching.

**Authentication:**  
Required

**Query Parameters (optional):**
| Name       | Type   | Example         | Description             |
|------------|--------|-----------------|-------------------------|
| action     | string | LOGIN           | Filter by action type   |
| timestamp  | date   | 2025-06-13      | Filter by log timestamp |
| ordering   | string | -timestamp      | Sort by field (e.g. -timestamp) |

**Response:**  
`200 OK`
```json
[
  {
    "id": 1,
    "user": 1,
    "action": "LOGIN",
    "metadata": {},
    "status": "PENDING",
    "timestamp": "2025-06-13T12:00:00Z"
  }
]
```

---

## 🔹 3. Update Log Status

**Endpoint:**  
`PATCH /logs/<log_id>/status/`

**Description:**  
Update the status (`PENDING`, `IN_PROGRESS`, `COMPLETED`) of a specific log.

**Authentication:**  
Required

**Request Body (JSON):**
```json
{
  "status": "IN_PROGRESS"
}
```

**Response:**  
`200 OK`
```json
{
  "id": 1,
  "user": 1,
  "action": "LOGIN",
  "metadata": {},
  "status": "IN_PROGRESS",
  "timestamp": "2025-06-13T12:00:00Z"
}
```

**Errors:**
- `404 Not Found` – Log not found for user.
- `400 Bad Request` – Invalid status value.
```json
{
  "error": "Invalid status"
}
```

---

## ✅ Status Enum Values

Valid values for `status`:

| Value         | Meaning               |
|---------------|------------------------|
| `PENDING`     | Action logged but not started |
| `IN_PROGRESS` | Action is ongoing     |
| `COMPLETED`   | Action is finished    |

---

## 🔐 Authentication

You must be logged in (via session or token). Use Django login or DRF token-based auth.
