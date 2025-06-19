# content_manager.py
import sqlite3

# Create or connect to database
conn = sqlite3.connect('college_tutor.db')
cursor = conn.cursor()

# Create table for educational content
cursor.execute('''CREATE TABLE IF NOT EXISTS content
                  (id INTEGER PRIMARY KEY, topic TEXT, content TEXT, level TEXT)''')

# Insert sample content
sample_content = [
    ("Machine Learning", "ML basics involve supervised and unsupervised learning.", "Intermediate"),
    ("Data Structures", "Arrays store data sequentially; trees are hierarchical.", "Beginner")
]
cursor.executemany("INSERT OR IGNORE INTO content (topic, content, level) VALUES (?, ?, ?)", sample_content)

# Commit changes
conn.commit()

def get_content(topic):
    cursor.execute("SELECT content FROM content WHERE topic = ?", (topic,))
    result = cursor.fetchone()
    return result[0] if result else "Content not found!"

# Example usage
if __name__ == "__main__":
    print(get_content("Machine Learning"))
    conn.close()