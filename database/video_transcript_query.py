import sqlite3

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
