-- ============================================================
-- PRODE MUNDIAL 2026 — Schema Supabase / PostgreSQL
-- Ejecutar en orden en el SQL Editor de Supabase
-- ============================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL,
    pin_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    grupo CHAR(1) NOT NULL,
    flag TEXT,
    seed INT
);

CREATE TABLE fixture (
    id INT PRIMARY KEY,
    fase TEXT NOT NULL,
    grupo CHAR(1),
    fecha_hora TIMESTAMPTZ NOT NULL,
    sede TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    equipo_local TEXT REFERENCES teams(id),
    equipo_visitante TEXT REFERENCES teams(id),
    ph_local TEXT,
    ph_visitante TEXT
);

CREATE TABLE picks_grupos (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    partido_id INT REFERENCES fixture(id),
    goles_local INT NOT NULL CHECK (goles_local >= 0 AND goles_local <= 20),
    goles_visitante INT NOT NULL CHECK (goles_visitante >= 0 AND goles_visitante <= 20),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, partido_id)
);

CREATE TABLE picks_eliminatorias (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    partido_id INT REFERENCES fixture(id),
    equipo_ganador TEXT REFERENCES teams(id),
    goles_local INT CHECK (goles_local >= 0 AND goles_local <= 20),
    goles_visitante INT CHECK (goles_visitante >= 0 AND goles_visitante <= 20),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, partido_id)
);

CREATE TABLE results (
    partido_id INT PRIMARY KEY REFERENCES fixture(id),
    goles_local INT,
    goles_visitante INT,
    ganador TEXT REFERENCES teams(id),
    finalizado BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO config(key, value) VALUES
    ('deadline_utc', '2026-06-11T16:00:00Z'),
    ('torneo_activo', 'true');

-- ============================================================
-- Row Level Security: bloquear escritura post-deadline
-- ============================================================

ALTER TABLE picks_grupos ENABLE ROW LEVEL SECURITY;
ALTER TABLE picks_eliminatorias ENABLE ROW LEVEL SECURITY;

-- Permitir lectura a todos los autenticados
CREATE POLICY "read_picks_grupos" ON picks_grupos FOR SELECT USING (true);
CREATE POLICY "read_picks_elim"   ON picks_eliminatorias FOR SELECT USING (true);

-- Permitir escritura solo antes del deadline
CREATE POLICY "write_picks_grupos" ON picks_grupos FOR INSERT WITH CHECK (
    NOW() < (SELECT value::TIMESTAMPTZ FROM config WHERE key = 'deadline_utc')
);
CREATE POLICY "write_picks_grupos_upd" ON picks_grupos FOR UPDATE USING (
    NOW() < (SELECT value::TIMESTAMPTZ FROM config WHERE key = 'deadline_utc')
);
CREATE POLICY "write_picks_elim" ON picks_eliminatorias FOR INSERT WITH CHECK (
    NOW() < (SELECT value::TIMESTAMPTZ FROM config WHERE key = 'deadline_utc')
);
CREATE POLICY "write_picks_elim_upd" ON picks_eliminatorias FOR UPDATE USING (
    NOW() < (SELECT value::TIMESTAMPTZ FROM config WHERE key = 'deadline_utc')
);
