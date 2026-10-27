"""
VietVoiceOmni - Database (SQLite)
Luu THAT: voices, history (co kind: speech/podcast/audiobook), hosts (mau + setting rieng),
podcasts, audiobooks, settings.
"""
import sqlite3
import json
import time
import threading
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "vietvoiceomni.db"
_lock = threading.Lock()

# 13 mau cho host (gioi han 13 host)
HOST_COLORS = [
    "#8b5cf6", "#ec4899", "#06b6d4", "#10b981", "#f59e0b",
    "#ef4444", "#3b82f6", "#a855f7", "#14b8a6", "#f97316",
    "#84cc16", "#e11d48", "#6366f1",
]
MAX_HOSTS = 13


def _conn():
    c = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def _ensure_col(c, table, col, decl):
    cols = [r[1] for r in c.execute(f"PRAGMA table_info({table})")]
    if col not in cols:
        c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")


def init_db():
    with _lock, _conn() as c:
        c.executescript(
            """
        CREATE TABLE IF NOT EXISTS voices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            ref_audio TEXT NOT NULL,
            description TEXT DEFAULT '',
            cfg_value REAL DEFAULT 1.3,
            timesteps INTEGER DEFAULT 23,
            pause REAL DEFAULT 0.6,
            speed REAL DEFAULT 1.0,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voice_name TEXT,
            text TEXT,
            params TEXT,
            mp3_path TEXT,
            duration REAL,
            n_sentences INTEGER,
            gen_time REAL,
            kind TEXT DEFAULT 'speech',
            title TEXT DEFAULT '',
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            voice_name TEXT,
            personality TEXT DEFAULT '',
            habits TEXT DEFAULT '',
            color TEXT DEFAULT '#8b5cf6',
            cfg_value REAL DEFAULT 1.3,
            timesteps INTEGER DEFAULT 23,
            pause REAL DEFAULT 0.4,
            speed REAL DEFAULT 1.0,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS podcasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            script TEXT,
            hosts TEXT,
            mp3_path TEXT,
            duration REAL,
            created_at REAL
        );
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        );
        """
        )
        # migration cot moi cho DB cu
        _ensure_col(c, "history", "kind", "TEXT DEFAULT 'speech'")
        _ensure_col(c, "history", "title", "TEXT DEFAULT ''")
        _ensure_col(c, "hosts", "color", "TEXT DEFAULT '#8b5cf6'")
        _ensure_col(c, "hosts", "cfg_value", "REAL DEFAULT 1.3")
        _ensure_col(c, "hosts", "timesteps", "INTEGER DEFAULT 23")
        _ensure_col(c, "hosts", "pause", "REAL DEFAULT 0.4")
        _ensure_col(c, "hosts", "speed", "REAL DEFAULT 1.0")


# ---------- VOICES ----------
def add_voice(name, ref_audio, description="", cfg_value=1.3, timesteps=23, pause=0.6, speed=1.0):
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO voices (name,ref_audio,description,cfg_value,timesteps,pause,speed,created_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (name, ref_audio, description, cfg_value, timesteps, pause, speed, time.time()),
        )

def list_voices():
    with _lock, _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM voices ORDER BY created_at DESC")]

def get_voice(name):
    with _lock, _conn() as c:
        r = c.execute("SELECT * FROM voices WHERE name=?", (name,)).fetchone()
        return dict(r) if r else None

def delete_voice(name):
    with _lock, _conn() as c:
        c.execute("DELETE FROM voices WHERE name=?", (name,))


# ---------- HISTORY (kind: speech / podcast / audiobook) ----------
def add_history(voice_name, text, params: dict, mp3_path, duration, n_sentences, gen_time,
                kind="speech", title=""):
    with _lock, _conn() as c:
        c.execute(
            "INSERT INTO history (voice_name,text,params,mp3_path,duration,n_sentences,gen_time,kind,title,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (voice_name, text, json.dumps(params, ensure_ascii=False), mp3_path,
             duration, n_sentences, gen_time, kind, title, time.time()),
        )

def list_history(limit=100, kind=None):
    with _lock, _conn() as c:
        if kind:
            return [dict(r) for r in c.execute(
                "SELECT * FROM history WHERE kind=? ORDER BY created_at DESC LIMIT ?", (kind, limit))]
        return [dict(r) for r in c.execute(
            "SELECT * FROM history ORDER BY created_at DESC LIMIT ?", (limit,))]

def delete_history(hid):
    with _lock, _conn() as c:
        c.execute("DELETE FROM history WHERE id=?", (hid,))


# ---------- HOSTS (Podcast: mau + setting rieng) ----------
def add_host(name, voice_name, personality="", habits="", color="#8b5cf6",
             cfg_value=1.3, timesteps=23, pause=0.4, speed=1.0):
    with _lock, _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO hosts "
            "(name,voice_name,personality,habits,color,cfg_value,timesteps,pause,speed,created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (name, voice_name, personality, habits, color, cfg_value, timesteps, pause, speed, time.time()),
        )

def list_hosts():
    with _lock, _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM hosts ORDER BY created_at ASC")]

def get_host(name):
    with _lock, _conn() as c:
        r = c.execute("SELECT * FROM hosts WHERE name=?", (name,)).fetchone()
        return dict(r) if r else None

def count_hosts():
    with _lock, _conn() as c:
        return c.execute("SELECT COUNT(*) FROM hosts").fetchone()[0]

def next_host_color():
    """Mau ke tiep chua dung (theo thu tu 13 mau)."""
    used = {h["color"] for h in list_hosts()}
    for col in HOST_COLORS:
        if col not in used:
            return col
    return HOST_COLORS[len(list_hosts()) % len(HOST_COLORS)]

def delete_host(name):
    with _lock, _conn() as c:
        c.execute("DELETE FROM hosts WHERE name=?", (name,))


# ---------- PODCASTS ----------
def add_podcast(title, script, hosts: list, mp3_path, duration):
    with _lock, _conn() as c:
        c.execute(
            "INSERT INTO podcasts (title,script,hosts,mp3_path,duration,created_at) VALUES (?,?,?,?,?,?)",
            (title, script, json.dumps(hosts, ensure_ascii=False), mp3_path, duration, time.time()),
        )

def list_podcasts():
    with _lock, _conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM podcasts ORDER BY created_at DESC")]


# ---------- SETTINGS ----------
_DEFAULTS = {
    "default_cfg": "1.3",
    "default_steps": "23",
    "default_pause": "0.6",
    "default_speed": "1.0",
    "master_mode": "raw",        # raw | clean
    "mp3_bitrate": "192k",
    "theme": "dark",
    "accent": "violet",
}

def get_setting(key, default=None):
    with _lock, _conn() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        if r:
            return r[0]
    return _DEFAULTS.get(key, default)

def set_setting(key, value):
    with _lock, _conn() as c:
        c.execute("INSERT OR REPLACE INTO settings (key,value) VALUES (?,?)", (key, str(value)))

def all_settings():
    out = dict(_DEFAULTS)
    with _lock, _conn() as c:
        for r in c.execute("SELECT key,value FROM settings"):
            out[r[0]] = r[1]
    return out
