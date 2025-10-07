---
title: "Automated Vehicle Parking Management System (AVPMS)"
author: "varun"
date: "2025-10-07"
output:
  github_document: default
---

> **Stack**: Python • Tkinter • MySQL • PaddleOCR 
> **Users**: Security Guard (Gate), Campus Member (Student/Faculty/Management), Admin

---

# 1. What this project does (TL;DR)
A desktop app for college parking that **reads license plates with PaddleOCR**, checks the **MySQL** database for verified members, **allocates/free slots** in real-time, and lets **admins** verify profiles and handle **flags** when the lot is full or something looks suspicious.

---

# 2. System Overview

## 2.1 Roles & Capabilities
- **Security Guard (Gate):** Login → scan/upload vehicle image → OCR → DB match → allocate slot (or raise flag) → process exits.
- **Campus Member:** Register/login → submit ID + photo for verification → see assigned slot if/when guard allocates.
- **Admin:** Verify profiles, resolve flags, manage slots/users, view dashboards & trends.

## 2.2 Core Flows
1. **Registration & Verification**
   - Choose role → register → email verify (optional for demo) → login → **Submit ID & profile photo** → admin approves → features unlock.
2. **Gate Entry**
   - Guard captures or uploads image → **PaddleOCR** reads plate → **normalize** plate → DB lookup.
   - If **member + verified + slot available** → allocate slot → create active parking event.
   - If **no slot** → raise **flag** to admin.
   - If **not in DB / unverified** → **Access Denied** message.
3. **Exit**
   - Guard scans/enters plate → find active event → **mark exited** → **free slot**.

---


---




## 4.5 Schema
```sql
i have created database parking_management but to create below tables

CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  college_id VARCHAR(32) UNIQUE NOT NULL,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(160) UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('member','guard','admin') NOT NULL,
  is_email_verified BOOL DEFAULT FALSE,
  is_profile_verified BOOL DEFAULT FALSE,
  mobile VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  plate_number VARCHAR(20) UNIQUE NOT NULL,
  is_active BOOL DEFAULT TRUE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE verifications (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  id_image_url VARCHAR(255),
  profile_image_url VARCHAR(255),
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  reviewer_id BIGINT,
  reviewed_at DATETIME,
  notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (reviewer_id) REFERENCES users(id)
);

CREATE TABLE slots (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(20) UNIQUE NOT NULL,
  zone VARCHAR(20),
  level VARCHAR(20),
  status ENUM('available','occupied','reserved') DEFAULT 'available',
  last_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE parking_events (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  vehicle_id BIGINT NOT NULL,
  slot_id BIGINT NOT NULL,
  guard_user_id BIGINT NOT NULL,
  entry_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  exit_time DATETIME,
  status ENUM('active','exited') DEFAULT 'active',
  ocr_plate_text VARCHAR(32),
  ocr_confidence DECIMAL(5,2),
  FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
  FOREIGN KEY (slot_id) REFERENCES slots(id),
  FOREIGN KEY (guard_user_id) REFERENCES users(id)
);

CREATE TABLE flags (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  vehicle_id BIGINT,
  raised_by_guard_id BIGINT NOT NULL,
  reason ENUM('no_slots','suspicious','mismatch','other') NOT NULL,
  status ENUM('open','closed') DEFAULT 'open',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  closed_by_admin_id BIGINT,
  resolution_note TEXT,
  closed_at DATETIME,
  FOREIGN KEY (vehicle_id) REFERENCES vehicles(id),
  FOREIGN KEY (raised_by_guard_id) REFERENCES users(id),
  FOREIGN KEY (closed_by_admin_id) REFERENCES users(id)
);

CREATE INDEX idx_vehicle_plate ON vehicles (plate_number);
CREATE INDEX idx_slot_status ON slots (status);
CREATE INDEX idx_parking_active ON parking_events (status, entry_time);
```


# 5. UI & Design System (Glassmorphism + Gradients)

> Tkinter is not natively glass; we **simulate glassmorphism**. Shadows are soft blurred rounded rectangles placed behind cards.

## 5.2 Layout
- **Landing/Auth**: Center a glass card (max width 520). Background = gradient with subtle animated scan lines (optional).
- **Dashboards**: 3–4 KPI chips (small glass cards) + one large card for tables or maps.
- **Guard Scan**: Left = live preview card; Right = result card (plate, confidence, actions).
- **Slots**: Grid of small glass tiles; **green = available**, **red = occupied**, **yellow = reserved**.

## 5.3 Interactions & Motion (Lightweight)
- Fade‑in app window: gradually increase `wm_attributes('-alpha')` from 0.0→1.0.
- Scan button pulse (scale or shadow intensity) while OCR running.
- Progress ring during OCR; disable buttons to prevent double submit.



# 6. Services (Core Logic)

## 6.1 OCR (PaddleOCR)
```python
# services/ocr_service.py
from paddleocr import PaddleOCR
import re

class PlateOCR:
    def __init__(self):
        self.ocr = PaddleOCR(lang='en', use_angle_cls=True, use_gpu=False)

    def extract_plate(self, image_path):
        result = self.ocr.ocr(image_path, cls=True)
        texts = []
        for line in result:
            for _, (text, conf) in line:
                texts.append((text, conf))
        if not texts:
            return "", 0.0
        raw, conf = max(texts, key=lambda x: x[1])
        raw = re.sub(r'[^A-Za-z0-9]', '', raw.upper())
        m = re.search(r'[A-Z]{2}\d{1,2}[A-Z]{0,2}\d{3,4}', raw)
        plate = m.group(0) if m else raw
        return plate, float(conf)
```

## 6.2 Parking Service
```python
# services/parking_service.py
import mysql.connector
from datetime import datetime

class ParkingService:
    def __init__(self, conn):
        self.conn = conn

    def find_vehicle(self, plate):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("""
            SELECT v.id AS vehicle_id, u.id AS user_id, u.is_profile_verified
            FROM vehicles v JOIN users u ON u.id=v.user_id
            WHERE v.plate_number=%s AND v.is_active=1
        """, (plate,))
        return cur.fetchone()

    def get_available_slots(self):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT id, code FROM slots WHERE status='available' ORDER BY code")
        return cur.fetchall()

    def allocate(self, vehicle_id, slot_id, guard_user_id, ocr_plate_text=None, ocr_conf=None):
        cur = self.conn.cursor()
        cur.execute("SELECT status FROM slots WHERE id=%s FOR UPDATE", (slot_id,))
        row = cur.fetchone()
        if not row or row[0] != 'available':
            self.conn.rollback()
            raise ValueError("Slot not available")
        cur.execute("""
            INSERT INTO parking_events (vehicle_id, slot_id, guard_user_id, ocr_plate_text, ocr_confidence)
            VALUES (%s,%s,%s,%s,%s)
        """, (vehicle_id, slot_id, guard_user_id, ocr_plate_text, ocr_conf))
        cur.execute("UPDATE slots SET status='occupied' WHERE id=%s", (slot_id,))
        self.conn.commit()

    def process_exit(self, plate):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("""
            SELECT pe.id, pe.slot_id FROM parking_events pe
            JOIN vehicles v ON v.id = pe.vehicle_id
            WHERE v.plate_number=%s AND pe.status='active'
            ORDER BY pe.entry_time DESC LIMIT 1
        """, (plate,))
        ev = cur.fetchone()
        if not ev:
            return False
        cur2 = self.conn.cursor()
        cur2.execute("UPDATE parking_events SET status='exited', exit_time=%s WHERE id=%s",
                     (datetime.now(), ev['id']))
        cur2.execute("UPDATE slots SET status='available' WHERE id=%s", (ev['slot_id'],))
        self.conn.commit()
        return True
```

## 6.3 Auth Service
```python
# services/auth_service.py
import bcrypt, mysql.connector

class AuthService:
    def __init__(self, conn):
        self.conn = conn

    def register(self, college_id, full_name, email, password, role):
        ph = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO users (college_id, full_name, email, password_hash, role)
            VALUES (%s,%s,%s,%s,%s)
        """, (college_id, full_name, email, ph, role))
        self.conn.commit()

    def login(self, email, password):
        cur = self.conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        u = cur.fetchone()
        if not u:
            return None
        if not bcrypt.checkpw(password.encode(), u['password_hash'].encode()):
            return None
        return u
```

---

# 7. Tkinter Screens (What to build)

## 7.1 Common
- **Landing**: glass card with 3 buttons (Security Guard / Campus Member / College Management).  
- **Auth**: Tabbed Login/Register; role-aware registration fields.  
- **Verify Profile**: Upload ID & profile photo → submit → status chip.

## 7.2 Security Guard
- **Dashboard**: KPI row (Vehicles Inside, Free Slots, Today Entries, Open Flags). Quick actions: **Scan Vehicle**, **Parking Map**, **Raise Flag**.
- **Vehicle Identification**: camera preview (OpenCV `VideoCapture`) + Upload; button **Read Plate** → show plate + confidence; action buttons: **Allocate Slot** (dropdown), **Raise Flag**, **Deny**.
- **Parking Slots**: grid of cards; search/filter by zone/level. Color coding.
- **Exit**: enter/scan plate → confirm exit.
- **Flags**: create/view flags; status.

## 7.3 Member
- **Dashboard**: verification status, **current assigned slot** (if any), recent history.
- **Assigned Slot**: read-only slot info, entry time.
- **My Vehicles**: list/add plates.

## 7.4 Admin
- **Dashboard**: totals + trends (day-of-week fill, peak hours heatmap [can be a simple colored grid now]).
- **Verification Queue**: table with pending users → open panel to approve/reject.
- **Flags**: open flags with actions; add resolution note.
- **Slots Manager**: CRUD + bulk import.
- **Users & Vehicles**: search, view, deactivate/reactivate.

---


# 9. Demo Script (for your viva)
1. **Login as Admin** → open **Verification Queue**, show pending user → **Approve**.
2. **Login as Guard** → open **Scan** → upload car image → OCR reads plate → **Allocate Slot**.
3. **Login as Member** → open **Assigned Slot** → see slot code.
4. **Back to Guard** → process **Exit** → slot becomes **available** again.
5. **Admin** → open **Flags** → resolve an open flag.

---

# 10. Testing & Edge Cases
- OCR confidence < 0.70 → prompt re-scan or manual plate entry.
- Duplicate plate on register → show clear error (unique index).
- Race condition on slot allocation → `SELECT ... FOR UPDATE` as shown.
- Member not verified → cannot see **Assigned Slot**; Guard sees **Access Denied**.
- Network/DB down → show toast and retry.

---

# 11. Security Notes
- Hash passwords with **bcrypt**; never store plain text.
- Use least-privilege MySQL user.
- Log admin/guard actions to an audit trail if needed.
- Store ID/Profile images in a local folder or S3-like bucket; reference by URL/path.

---

# 12. Future Enhancements
- Plate **detector** model before OCR (for better ROI).
- Role-based **JWT** + API server (FastAPI) if you move beyond local desktop.
- Analytics with **SQLite cache** for read-heavy dashboards.
- Notifications to member app (if you add a mobile client).

---


