-- Installation de pgcrypto pour générer des UUIDs
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Changements a apporter
CREATE TABLE sensor_data (
    uid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    name VARCHAR(100) NOT NULL, -- N'est pas dans l'exemple mais est demandé

    description VARCHAR(255),
    unit VARCHAR(10) NOT NULL,
    min_value FLOAT NOT NULL,
    max_value FLOAT NOT NULL,
    delta_value FLOAT DEFAULT 1,
    period INTEGER NOT NULL,
    min_period INTEGER DEFAULT 60,
    max_period INTEGER DEFAULT 3600,
    read_only BOOLEAN DEFAULT FALSE,
    value FLOAT DEFAULT 0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- pour stocker les valeurs des simulation
CREATE TABLE sensor_history (
    id SERIAL PRIMARY KEY,
    sensor_uid UUID REFERENCES sensor_data(uid) ON DELETE CASCADE,
    value FLOAT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates de capteurs
CREATE TABLE sensor_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,  -- Nom du modèle
    description VARCHAR(255),
    unit VARCHAR(10) NOT NULL,
    min_value FLOAT NOT NULL,
    max_value FLOAT NOT NULL,
    delta_value FLOAT DEFAULT 1,
    period INTEGER NOT NULL,
    min_period INTEGER DEFAULT 60,
    max_period INTEGER DEFAULT 3600,
    read_only BOOLEAN DEFAULT FALSE
);
