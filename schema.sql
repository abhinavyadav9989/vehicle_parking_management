
---creating database `parking_management`

USE parking_management;

CREATE TABLE IF NOT EXISTS users (
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

CREATE TABLE IF NOT EXISTS vehicles (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  plate_number VARCHAR(20) UNIQUE NOT NULL,
  is_active BOOL DEFAULT TRUE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS verifications (
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

CREATE TABLE IF NOT EXISTS slots (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(20) UNIQUE NOT NULL,
  zone VARCHAR(20),
  level VARCHAR(20),
  status ENUM('available','occupied','reserved') DEFAULT 'available',
  last_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parking_events (
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

CREATE TABLE IF NOT EXISTS flags (
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

-- Note: Some MySQL versions don't support IF NOT EXISTS for CREATE INDEX
-- Run these once; rerunning may cause duplicate key errors if indexes already exist
CREATE INDEX idx_vehicle_plate ON vehicles (plate_number);
CREATE INDEX idx_slot_status ON slots (status);
CREATE INDEX idx_parking_active ON parking_events (status, entry_time);


