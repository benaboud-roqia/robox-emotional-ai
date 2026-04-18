import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "robox.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            created_at TEXT,
            updated_at TEXT,
            lang TEXT DEFAULT 'fr',
            personality TEXT DEFAULT 'auto'
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id TEXT,
            role TEXT,
            content TEXT,
            sentiment TEXT,
            vocal_emotion TEXT,
            created_at TEXT,
            FOREIGN KEY (conv_id) REFERENCES conversations(id)
        );
    """)
    conn.commit()
    conn.close()

def create_conversation(conv_id, title, lang="fr", personality="auto"):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO conversations (id,title,created_at,updated_at,lang,personality) VALUES (?,?,?,?,?,?)",
        (conv_id, title, now, now, lang, personality)
    )
    conn.commit()
    conn.close()

def save_message(conv_id, role, content, sentiment=None, vocal_emotion=None):
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute(
        "INSERT INTO messages (conv_id,role,content,sentiment,vocal_emotion,created_at) VALUES (?,?,?,?,?,?)",
        (conv_id, role, content,
         json.dumps(sentiment) if sentiment else None,
         vocal_emotion, now)
    )
    conn.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id))
    conn.commit()
    conn.close()

def update_conv_title(conv_id, title):
    conn = get_db()
    conn.execute("UPDATE conversations SET title=? WHERE id=?", (title, conv_id))
    conn.commit()
    conn.close()

def get_all_conversations():
    conn = get_db()
    rows = conn.execute(
        "SELECT c.*, COUNT(m.id) as msg_count FROM conversations c "
        "LEFT JOIN messages m ON c.id=m.conv_id AND m.role='user' "
        "GROUP BY c.id ORDER BY c.updated_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_conversation_messages(conv_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM messages WHERE conv_id=? ORDER BY created_at ASC",
        (conv_id,)
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        m = dict(r)
        if m.get("sentiment"):
            try: m["sentiment"] = json.loads(m["sentiment"])
            except: pass
        result.append(m)
    return result

def delete_conversation(conv_id):
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE conv_id=?", (conv_id,))
    conn.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
    conn.commit()
    conn.close()

# Init au démarrage
init_db()
