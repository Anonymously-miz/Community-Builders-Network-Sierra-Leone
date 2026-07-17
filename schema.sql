-- ================================================================
-- Community Builders Network - Sierra Leone
-- MySQL schema
--
-- Run:
--   mysql -u root -p < database/schema.sql
-- ================================================================

CREATE DATABASE IF NOT EXISTS cbn_sierra_leone
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE cbn_sierra_leone;

-- ---------- Contact form submissions ----------
CREATE TABLE IF NOT EXISTS contact_submissions (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  full_name     VARCHAR(150) NOT NULL,
  email         VARCHAR(150) NOT NULL,
  phone         VARCHAR(50),
  subject       VARCHAR(200),
  message       TEXT NOT NULL,
  status        ENUM('new','read','replied','archived') DEFAULT 'new',
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- ---------- Volunteer applications ----------
CREATE TABLE IF NOT EXISTS volunteer_applications (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  first_name    VARCHAR(100) NOT NULL,
  last_name     VARCHAR(100) NOT NULL,
  email         VARCHAR(150) NOT NULL,
  phone         VARCHAR(50),
  role          VARCHAR(150),
  availability  VARCHAR(150),
  message       TEXT,
  status        ENUM('new','reviewing','accepted','rejected','archived') DEFAULT 'new',
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_created (created_at)
) ENGINE=InnoDB;

-- ---------- Partnership enquiries ----------
CREATE TABLE IF NOT EXISTS partner_enquiries (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  organisation  VARCHAR(200) NOT NULL,
  org_type      VARCHAR(100),
  contact_name  VARCHAR(150) NOT NULL,
  contact_email VARCHAR(150) NOT NULL,
  interest_area VARCHAR(100),
  budget_range  VARCHAR(100),
  message       TEXT,
  status        ENUM('new','contacted','in_progress','closed') DEFAULT 'new',
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status)
) ENGINE=InnoDB;

-- ---------- Newsletter subscribers ----------
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  email         VARCHAR(150) NOT NULL UNIQUE,
  active        TINYINT(1) DEFAULT 1,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_active (active)
) ENGINE=InnoDB;

-- ---------- Projects (dynamic content) ----------
CREATE TABLE IF NOT EXISTS projects (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(200) NOT NULL,
  slug          VARCHAR(200) NOT NULL UNIQUE,
  category      VARCHAR(50) NOT NULL,
  status        ENUM('current','past') NOT NULL DEFAULT 'current',
  location      VARCHAR(150),
  start_year    INT,
  end_year      INT,
  summary       TEXT,
  description   TEXT,
  image_url     VARCHAR(500),
  funded_pct    TINYINT DEFAULT 0,
  featured      TINYINT(1) DEFAULT 0,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_category (category),
  INDEX idx_featured (featured)
) ENGINE=InnoDB;

-- ---------- Blog posts ----------
CREATE TABLE IF NOT EXISTS blog_posts (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(250) NOT NULL,
  slug          VARCHAR(250) NOT NULL UNIQUE,
  category      VARCHAR(50) NOT NULL,
  author        VARCHAR(150),
  excerpt       TEXT,
  body          MEDIUMTEXT,
  image_url     VARCHAR(500),
  read_minutes  INT DEFAULT 5,
  published_at  DATE,
  featured      TINYINT(1) DEFAULT 0,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_category (category),
  INDEX idx_published (published_at),
  INDEX idx_featured (featured)
) ENGINE=InnoDB;

-- ---------- Events ----------
CREATE TABLE IF NOT EXISTS events (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  title         VARCHAR(250) NOT NULL,
  location      VARCHAR(200),
  event_date    DATE NOT NULL,
  event_time    VARCHAR(50),
  description   TEXT,
  cta_label     VARCHAR(50) DEFAULT 'Register',
  cta_url       VARCHAR(500) DEFAULT '#',
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_date (event_date)
) ENGINE=InnoDB;

-- ---------- Success stories ----------
CREATE TABLE IF NOT EXISTS success_stories (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  name          VARCHAR(150) NOT NULL,
  role          VARCHAR(150),
  quote         TEXT NOT NULL,
  image_url     VARCHAR(500),
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------- Admin users ----------
CREATE TABLE IF NOT EXISTS admin_users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(80) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name     VARCHAR(150),
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------- Admin sessions (simple token-based) ----------
CREATE TABLE IF NOT EXISTS admin_sessions (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  admin_id      INT NOT NULL,
  token         CHAR(64) NOT NULL UNIQUE,
  expires_at    DATETIME NOT NULL,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (admin_id) REFERENCES admin_users(id) ON DELETE CASCADE,
  INDEX idx_token (token),
  INDEX idx_expires (expires_at)
) ENGINE=InnoDB;
