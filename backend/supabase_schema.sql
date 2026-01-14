CREATE TABLE IF NOT EXISTS papers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT[] NOT NULL DEFAULT '{}',
    summary TEXT,
    published TIMESTAMPTZ NOT NULL,
    pdf_url TEXT,
    key_concepts TEXT[] DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    target_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
    edge_type TEXT NOT NULL,  
    evidence TEXT,
    strength FLOAT DEFAULT 1.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    role TEXT NOT NULL,  
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source_id);
CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target_id);
