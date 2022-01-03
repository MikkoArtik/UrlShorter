CREATE TABLE urls(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    origin_url TEXT UNIQUE NOT NULL,
    short_url VARCHAR UNIQUE NOT NULL,
    registration_date TIMESTAMP NOT NULL,
    expiration_days INTEGER DEFAULT 1,
    is_active BOOL DEFAULT TRUE
);
