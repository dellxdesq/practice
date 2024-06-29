import sqlite3

class VideoTranscriptDB:
    def __init__(self, db_name="transcripts.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY,
                    url TEXT UNIQUE
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS segments (
                    id INTEGER PRIMARY KEY,
                    video_id INTEGER,
                    start_time TEXT,
                    text TEXT,
                    FOREIGN KEY(video_id) REFERENCES videos(id)
                )
            """)

    def insert_video(self, url):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM videos WHERE url = ?", (url,))
            result = cursor.fetchone()
            if result:
                return None  # URL already exists in the database
            cursor.execute("INSERT INTO videos (url) VALUES (?)", (url,))
            return cursor.lastrowid

    def insert_segment(self, video_id, start_time, text):
        with self.conn:
            self.conn.execute("""
                INSERT INTO segments (video_id, start_time, text)
                VALUES (?, ?, ?)
            """, (video_id, start_time, text))

    def get_segments(self, video_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT start_time, text FROM segments WHERE video_id = ?", (video_id,))
        return cursor.fetchall()

class VideoTranscriptQuery:
    def __init__(self, db_name="transcripts.db"):
        self.conn = sqlite3.connect(db_name)

    def get_segments_by_url(self, url):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM videos WHERE url = ?", (url,))
        result = cursor.fetchone()
        if result:
            video_id = result[0]
            cursor.execute("SELECT start_time, text FROM segments WHERE video_id = ?", (video_id,))
            return cursor.fetchall()
        else:
            return None