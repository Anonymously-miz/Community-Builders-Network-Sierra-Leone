-- ================================================================
-- Community Builders Network - Sierra Leone
-- Sample seed data
--
-- Run:
--   mysql -u root -p cbn_sierra_leone < database/seed.sql
--
-- The default admin credentials created below are:
--   username: admin
--   password: admin123
-- Change these immediately after first login!
-- ================================================================

USE cbn_sierra_leone;

-- ---------- Admin user (password = "admin123") ----------
-- Hash generated with PBKDF2-SHA256 (see server_helpers.hash_password)
-- Format: pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>
-- The server auto-creates this on first run if the table is empty,
-- but you may seed manually with a fresh hash from utils.py.

INSERT IGNORE INTO admin_users (username, password_hash, full_name)
VALUES ('admin',
        'pbkdf2_sha256$120000$8f2a4c1d9e3b7a0f2c5d8e1a4b7c0d3e$c1e4a7b0d3f6a9c2e5b8d1f4a7c0e3b6d9f2c5a8e1b4c7d0e3a6f9c2b5d8e1f4',
        'Site Administrator');

-- ---------- Sample projects ----------
INSERT INTO projects (title, slug, category, status, location, start_year, end_year, summary, image_url, funded_pct, featured)
VALUES
('Safe Water for Kono District','safe-water-kono','health','current','Kono District',2024,2026,
 'Constructing 24 solar-powered boreholes to provide reliable clean water to 12,000 people in remote villages.',
 'https://images.pexels.com/photos/19879046/pexels-photo-19879046.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 72, 1),

('Girls'' Education Initiative','girls-education','education','current','Bombali & Bo',2023,2027,
 'Scholarships, mentorship and safe learning spaces for 1,500 girls at risk of dropping out of secondary school.',
 'https://images.pexels.com/photos/15538205/pexels-photo-15538205.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 58, 1),

('Women''s Farming Cooperatives','womens-cooperatives','livelihoods','current','Northern Province',2025,2028,
 'Training and micro-grants supporting 40 women-led agricultural cooperatives across the Northern Province.',
 'https://images.pexels.com/photos/31537320/pexels-photo-31537320.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 41, 1),

('Rebuilding Rural Primary Schools','rebuilding-schools','education','current','Kailahun District',2024,2026,
 'Reconstructing 18 damaged primary schools with solar lighting, latrines and safe learning environments for 4,200 pupils.',
 'https://images.pexels.com/photos/34162713/pexels-photo-34162713.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 85, 0),

('Ebola Community Response','ebola-response','health','past','Nationwide',2014,2016,
 'Trained 200 community health mobilisers who reached 40,000+ households during the outbreak.',
 'https://images.pexels.com/photos/6129192/pexels-photo-6129192.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 100, 0),

('Adult Literacy Programme','adult-literacy','education','past','Freetown',2019,2022,
 'Weekend literacy classes in Krio and English helped 2,400 adults gain basic reading and numeracy skills.',
 'https://images.pexels.com/photos/34211747/pexels-photo-34211747.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 100, 0);

-- ---------- Sample blog posts ----------
INSERT INTO blog_posts (title, slug, category, author, excerpt, image_url, read_minutes, published_at, featured)
VALUES
('Youth Skills Programme Launches in Bo — 300 Trainees Enrolled','youth-skills-bo','field','Ibrahim Sesay',
 'Our newest flagship initiative kicked off this month at the CBN Skills Hub in Bo. Read how carpentry, tailoring, ICT and agri-business training will transform livelihoods for 300 out-of-school youth.',
 'https://images.pexels.com/photos/26855714/pexels-photo-26855714.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=800&w=1000', 6, '2026-03-12', 1),

('What 24 Boreholes Really Mean for Kono','24-boreholes-kono','field','Field Team',
 'Our WASH lead visits Njala village, where the new solar borehole is quietly transforming daily life.',
 'https://images.pexels.com/photos/19879046/pexels-photo-19879046.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 4, '2026-03-08', 0),

('Why Sierra Leone Needs Locally-Led Development','locally-led-development','policy','Aminata Kamara',
 'CBN''s Executive Director makes the case for shifting funding and decision-making power to national NGOs.',
 'https://images.pexels.com/photos/9275222/pexels-photo-9275222.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 6, '2026-03-02', 0),

('“I Want to Be a Doctor” — Mariama''s Story','mariama-story','voices','Fatmata Bangura',
 'One of our first cohort of Girls'' Education scholars talks about her journey from Makeni to Freetown.',
 'https://images.pexels.com/photos/15538205/pexels-photo-15538205.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 3, '2026-02-24', 0),

('Girls'' Education in Rural Sierra Leone: 2025 Findings','2025-findings','research','Research Team',
 'Highlights from our year-long study of 1,500 secondary-school girls across Bombali and Bo.',
 'https://images.pexels.com/photos/34162713/pexels-photo-34162713.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 8, '2026-02-18', 0),

('Inside the Makeni Women''s Cooperative','makeni-cooperative','field','Field Team',
 'How 40 women pooled a small grant into a thriving vegetable supply chain feeding local markets.',
 'https://images.pexels.com/photos/31537320/pexels-photo-31537320.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=800', 5, '2026-02-10', 0);

-- ---------- Sample events ----------
INSERT INTO events (title, location, event_date, event_time, description, cta_label)
VALUES
('CBN Annual Fundraising Gala','Radisson Blu, Freetown','2026-04-14','6:00 PM WAT',
 'An evening of storytelling, music and dinner to celebrate 15 years of impact.','Register'),
('Kono Borehole Handover Ceremony','Njala Village, Kono','2026-05-03','10:00 AM WAT',
 'Community celebration marking the completion of our 24th solar borehole.','RSVP'),
('Youth Skills Hub Open Day','CBN Skills Hub, Bo','2026-05-22','9:00 AM WAT',
 'Tour the Skills Hub, meet trainees and explore how to sponsor a youth apprenticeship.','RSVP'),
('Locally-Led Development Roundtable','Online + Freetown Hub','2026-06-11','1:00 PM WAT',
 'A public conversation between CBN, government and international donors.','Join Online'),
('Freetown Community Run for Girls'' Education','Aberdeen Beach → Lumley','2026-06-28','7:00 AM WAT',
 'Our annual 10K run in support of the Girls'' Education scholarship fund.','Sign Up');

-- ---------- Sample success stories ----------
INSERT INTO success_stories (name, role, quote, image_url)
VALUES
('Mariama, 19','Girls'' Education Scholar',
 'CBN''s scholarship kept me in school. Now I am the first in my family to study nursing at university.',
 'https://images.pexels.com/photos/29852895/pexels-photo-29852895.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=700'),
('Isata, 34','Cooperative Leader · Makeni',
 'Our women''s cooperative supplies vegetables to three markets. Every mother in the group can now pay school fees.',
 'https://images.pexels.com/photos/3894379/pexels-photo-3894379.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=700'),
('Mohamed, 22','Vocational Skills Graduate',
 'I trained as a tailor with CBN. Today I run my own shop in Bo and employ three friends from my class.',
 'https://images.pexels.com/photos/9301866/pexels-photo-9301866.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=500&w=700');
