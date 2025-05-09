CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    password TEXT NOT NULL,
    is_guest BOOLEAN NOT NULL DEFAULT FALSE,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

CREATE TABLE events (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    time VARCHAR(10) NOT NULL,
    location VARCHAR(255) NOT NULL,
    image_url TEXT NOT NULL
);

CREATE TABLE ticket_types (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(36) REFERENCES events(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    available INTEGER NOT NULL
);

CREATE TABLE tickets (
    id VARCHAR(36) PRIMARY KEY,
    event_id VARCHAR(36) REFERENCES events(id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    ticket_type_id VARCHAR(36) REFERENCES ticket_types(id) ON DELETE CASCADE,
    purchase_date TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    qrCode TEXT NOT NULL,
    attendee_name VARCHAR(100) NOT NULL,
    attendee_email VARCHAR(255) NOT NULL
);