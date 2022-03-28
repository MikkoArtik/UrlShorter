CREATE TABLE links (
    id SERIAL PRIMARY KEY,
    link TEXT UNIQUE NOT NULL,
    registration_date TIMESTAMP NOT NULL DEFAULT NOW(),
    days_count INT DEFAULT 0,
    short_id VARCHAR(7) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT true
);