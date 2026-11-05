#!/usr/bin/env python3
"""SQLite schema and small transactional helpers for Librarian Memory v1."""
from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

# Portable agent home: PI_CONFIG_DIR overrides the ~/.pi/agent default.
AGENT_HOME = Path(os.environ.get('PI_CONFIG_DIR', str(Path.home() / '.pi/agent')))
DB_PATH = AGENT_HOME / 'memory/memory.db'

def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')

def connect(path: str | Path = DB_PATH) -> sqlite3.Connection:
    p = Path(path).expanduser().resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(p), timeout=30)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA journal_mode=WAL')
    con.execute('PRAGMA busy_timeout=30000')
    init(con)
    return con

def init(con: sqlite3.Connection) -> None:
    con.executescript('''
CREATE TABLE IF NOT EXISTS records (
 id INTEGER PRIMARY KEY,
 scope TEXT NOT NULL,
 kind TEXT NOT NULL,
 text TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('candidate','active','superseded','expired')),
 source_session_id TEXT,
 source_entry_id TEXT,
 created TEXT NOT NULL,
 updated TEXT NOT NULL,
 verified_by_user INTEGER NOT NULL DEFAULT 0 CHECK(verified_by_user IN (0,1)),
 confidence REAL,
 supersedes INTEGER REFERENCES records(id),
 keys TEXT,
 observed_at TEXT,
 valid_from TEXT,
 invalid_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS records_source_entry_unique
 ON records(source_session_id, source_entry_id, kind);
CREATE INDEX IF NOT EXISTS records_filter_idx ON records(scope, kind, status, updated);
CREATE TABLE IF NOT EXISTS evidence (
 record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
 pointer TEXT NOT NULL,
 kind TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS evidence_record_idx ON evidence(record_id);
CREATE TABLE IF NOT EXISTS sessions_cursor (
 id INTEGER PRIMARY KEY CHECK(id=1),
 last_session_id TEXT,
 last_entry_id TEXT
);
INSERT OR IGNORE INTO sessions_cursor(id,last_session_id,last_entry_id) VALUES(1,NULL,NULL);
CREATE TABLE IF NOT EXISTS backfill_cursor (
 id INTEGER PRIMARY KEY CHECK(id=1),
 last_file TEXT,
 last_entry_id TEXT
);
INSERT OR IGNORE INTO backfill_cursor(id,last_file,last_entry_id) VALUES(1,NULL,NULL);
CREATE TABLE IF NOT EXISTS consolidation_runs (
 id INTEGER PRIMARY KEY,
 started TEXT NOT NULL,
 ended TEXT,
 batches INTEGER NOT NULL DEFAULT 0,
 accepted INTEGER NOT NULL DEFAULT 0,
 candidates INTEGER NOT NULL DEFAULT 0,
 rejected INTEGER NOT NULL DEFAULT 0,
 exit_status TEXT
);
CREATE TABLE IF NOT EXISTS retrieval_log (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 ts TEXT NOT NULL,
 query TEXT,
 scope TEXT,
 kind TEXT,
 status TEXT,
 returned_ids TEXT,
 bytes INTEGER NOT NULL DEFAULT 0
);
CREATE VIRTUAL TABLE IF NOT EXISTS records_fts USING fts5(
 text, kind, scope, content='records', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS records_ai AFTER INSERT ON records BEGIN
 INSERT INTO records_fts(rowid,text,kind,scope) VALUES(new.id,new.text,new.kind,new.scope);
END;
CREATE TRIGGER IF NOT EXISTS records_ad AFTER DELETE ON records BEGIN
 INSERT INTO records_fts(records_fts,rowid,text,kind,scope) VALUES('delete',old.id,old.text,old.kind,old.scope);
END;
CREATE TRIGGER IF NOT EXISTS records_au AFTER UPDATE ON records BEGIN
 INSERT INTO records_fts(records_fts,rowid,text,kind,scope) VALUES('delete',old.id,old.text,old.kind,old.scope);
 INSERT INTO records_fts(rowid,text,kind,scope) VALUES(new.id,new.text,new.kind,new.scope);
END;
CREATE VIRTUAL TABLE IF NOT EXISTS records_keys_fts USING fts5(
 keys, content='records', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS records_keys_ai AFTER INSERT ON records BEGIN
 INSERT INTO records_keys_fts(rowid,keys) VALUES(new.id,new.keys);
END;
CREATE TRIGGER IF NOT EXISTS records_keys_ad AFTER DELETE ON records BEGIN
 INSERT INTO records_keys_fts(records_keys_fts,rowid,keys) VALUES('delete',old.id,old.keys);
END;
CREATE TRIGGER IF NOT EXISTS records_keys_au AFTER UPDATE ON records BEGIN
 INSERT INTO records_keys_fts(records_keys_fts,rowid,keys) VALUES('delete',old.id,old.keys);
 INSERT INTO records_keys_fts(rowid,keys) VALUES(new.id,new.keys);
END;
''')
    # B1 (2026-11-15): review_state as an orthogonal column — no table rebuild needed.
    # 'conflict'/'quarantined' ride alongside lifecycle status (candidate/active/superseded/expired).
    cols = [r[1] for r in con.execute('PRAGMA table_info(records)').fetchall()]
    if 'review_state' not in cols:
        con.execute("ALTER TABLE records ADD COLUMN review_state TEXT NOT NULL DEFAULT 'none' "
                    "CHECK(review_state IN ('none','conflict','quarantined'))")
    # B4 (2026-11-15): validity fields (evidence-backed: Graphiti/Cognee practice) + fact-augmented keys.
    migrated = False
    for col in ('keys','observed_at','valid_from','invalid_at'):
        if col not in cols:
            con.execute(f'ALTER TABLE records ADD COLUMN {col} TEXT')
            migrated = True
    if migrated:
        # ALTER TABLE ADD COLUMN on the external-content FTS's content table goes stale
        # until rebuild (SQLite quirk: triggers then report 'database disk image is malformed').
        con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
        con.execute("INSERT INTO records_keys_fts(records_keys_fts) VALUES('rebuild')")
    # One-time backfill: existing records were observed/valid when created.
    con.execute('UPDATE records SET observed_at=created WHERE observed_at IS NULL')
    con.execute('UPDATE records SET valid_from=created WHERE valid_from IS NULL')
    # Rebuild the FTS index ONLY when it is out of sync with the records table —
    # never unconditionally on every connection open (2026-11-15 fix).
    n_records = con.execute('SELECT COUNT(*) FROM records').fetchone()[0]
    n_fts = con.execute('SELECT COUNT(*) FROM records_fts').fetchone()[0]
    if n_records != n_fts:
        con.execute("INSERT INTO records_fts(records_fts) VALUES('rebuild')")
    con.commit()

def insert_record(con, *, scope, kind, text, status='candidate', source_session_id=None,
                   source_entry_id=None, evidence_pointer=None, evidence_kind='session-entry',
                   confidence=None, verified_by_user=0, supersedes=None, keys=None):
    t = now()
    cur = con.execute('''INSERT OR IGNORE INTO records
      (scope,kind,text,status,source_session_id,source_entry_id,created,updated,verified_by_user,confidence,supersedes,keys,observed_at,valid_from)
      VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (scope,kind,text,status,source_session_id,source_entry_id,t,t,int(verified_by_user),confidence,supersedes,keys,t,t))
    if cur.rowcount == 0:
        row = con.execute('SELECT id FROM records WHERE source_session_id IS ? AND source_entry_id IS ? AND kind=?', (source_session_id,source_entry_id,kind)).fetchone()
        if row is None:
            # OR IGNORE also swallows CHECK failures — never report those as dedupe (oracle finding).
            raise sqlite3.IntegrityError('insert failed and no dedupe row matched (likely CHECK/constraint failure)')
        return int(row['id']), False
    rid = int(cur.lastrowid)
    if evidence_pointer:
        con.execute('INSERT INTO evidence(record_id,pointer,kind) VALUES(?,?,?)', (rid,evidence_pointer,evidence_kind))
    return rid, True
