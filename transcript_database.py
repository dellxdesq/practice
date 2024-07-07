import sqlite3
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import faiss
from datetime import datetime, timedelta
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
                    url TEXT,
                    FOREIGN KEY(video_id) REFERENCES videos(id)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tg_user (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    date_publication DATE
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    video_url TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES tg_user(id)
                )
            """)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY,
                    id_user INTEGER NOT NULL,
                    users_tokens INTEGER NOT NULL,
                    FOREIGN KEY(id_user) REFERENCES tg_user(id)
                )
            """)

    def insert_video(self, url):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM videos WHERE url = ?", (url,))
            result = cursor.fetchone()
            if result:
                return None  # URL уже существует в базе данных
            cursor.execute("INSERT INTO videos (url) VALUES (?)", (url,))
            return cursor.lastrowid

    def insert_segment(self, video_id, start_time, text, url):
        with self.conn:
            self.conn.execute("""
                INSERT INTO segments (video_id, start_time, text, url)
                VALUES (?, ?, ?, ?)
            """, (video_id, start_time, text, url))

    def get_segments(self, video_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT start_time, text FROM segments WHERE video_id = ?", (video_id,))
        return cursor.fetchall()

    def get_all_segments(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT text FROM segments")
        return [row[0] for row in cursor.fetchall()]

    def insert_tg_user(self, user_id, url, date_publication):
        try:
            with self.conn:
                self.conn.execute("""
                    INSERT INTO tg_user (user_id, url, date_publication)
                    VALUES (?,?,?)
                """, (user_id, url, date_publication))
                self.conn.commit()  # <--- Add this line
            print("Данные о пользователе успешно добавлены в таблицу tg_user.")
        except Exception as e:
            print(f"Ошибка при добавлении данных в таблицу tg_user: {str(e)}")

    def add_favorite(self, user_id, video_url):
        with self.conn:
            self.conn.execute("""
                INSERT INTO favorites (user_id, video_url)
                VALUES (?, ?)
            """, (user_id, video_url))
            self.conn.commit()

    def get_favorites(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT video_url FROM favorites WHERE user_id = ?", (user_id,))
        return [row[0] for row in cursor.fetchall()]

    def remove_favorite(self, user_id, video_url):
        with self.conn:
            self.conn.execute("""
                DELETE FROM favorites
                WHERE user_id = ? AND video_url = ?
            """, (user_id, video_url))
            self.conn.commit()

    def get_new_users_by_days(self, days):
        current_date = datetime.now()
        start_date = current_date - timedelta(days=days)

        cursor = self.conn.execute("""
            SELECT user_id, MIN(date_publication) AS earliest_date
            FROM tg_user
            WHERE date_publication >= ?
            GROUP BY user_id
        """, (start_date,))

        return cursor.fetchall()

    def get_activities_by_date(self, date):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_id, GROUP_CONCAT(url) AS videos
            FROM tg_user
            WHERE date(date_publication) = ?
            GROUP BY user_id
        """, (date.strftime("%Y-%m-%d"),))
        return cursor.fetchall()

    def add_tokens(self, user_id, token_count):
        cursor = self.conn.cursor()
        cursor.execute("SELECT users_tokens FROM tokens WHERE id_user = ?", (user_id,))
        existing_tokens = cursor.fetchone()
        if existing_tokens:
            new_token_count = existing_tokens[0] + token_count
            cursor.execute("UPDATE tokens SET users_tokens = ? WHERE id_user = ?", (new_token_count, user_id))
        else:
            cursor.execute("INSERT INTO tokens (id_user, users_tokens) VALUES (?, ?)", (user_id, token_count))
        self.conn.commit()

    def get_user_tokens(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT users_tokens FROM tokens WHERE id_user = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0


    def decrease_user_tokens(self, user_id):
        cursor = self.conn.execute("SELECT users_tokens FROM tokens WHERE id_user = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            current_tokens = result[0]
            if current_tokens > 0:
                self.conn.execute("UPDATE tokens SET users_tokens = ? WHERE id_user = ?", (current_tokens - 1, user_id))
                self.conn.commit()
                return True
            else:
                return False
        else:
            return False

    def insert_user_tokens(self, user_id, tokens):
        try:
            self.conn.execute("INSERT INTO tokens (id_user, users_tokens) VALUES (?, ?)", (user_id, tokens))
            self.conn.commit()
        except sqlite3.IntegrityError:
            # User already exists, do nothing
            pass

    def user_exists(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM tokens WHERE id_user = ?", (user_id,))
        return cursor.fetchone() is not None

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