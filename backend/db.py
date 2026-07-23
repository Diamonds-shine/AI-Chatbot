import sqlite3

# Create database connection
conn = sqlite3.connect("chatbot.db", check_same_thread=False)

# Create cursor
cursor = conn.cursor()

# Create chat_history table
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Save changes
conn.commit()

# -----------------------------
# Save Chat Message
# -----------------------------
def save_message(role, message):
    cursor.execute(
        """
        INSERT INTO chat_history(role, message)
        VALUES (?, ?)
        """,
        (role, message)
    )
    conn.commit()

# -----------------------------
# Get Chat History
# -----------------------------
def get_chat_history():
    cursor.execute("""
        SELECT role, message, timestamp
        FROM chat_history
        ORDER BY id
    """)
    return cursor.fetchall()
# -----------------------------
# Clear Chat History
# -----------------------------
def clear_chat_history():
    cursor.execute("DELETE FROM chat_history")
    conn.commit()