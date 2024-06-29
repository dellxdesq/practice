from database import VideoTranscriptDB, VideoTranscriptQuery
from parser import TranscriptParser

class VideoTranscriptApp:
    def __init__(self):
        self.db = VideoTranscriptDB()
        self.query = VideoTranscriptQuery()
        self.parser = TranscriptParser()

    def add_video(self, video_url):
        video_id = self.db.insert_video(video_url)
        if video_id is None:
            print("Это видео уже есть в базе данных.")
            return

        transcript = self.parser.get_transcript(video_url)
        if transcript:
            merged_transcript = self.parser.merge_transcripts(transcript)
            for entry in merged_transcript:
                start_time = self.parser.format_time(entry['start'])
                text = entry['text']
                self.db.insert_segment(video_id, start_time, text)
                print(f"{start_time}: {text}")
        else:
            print("Расшифровка на русском языке недоступна для данного видео.")

    def query_segments(self, video_url):
        segments = self.query.get_segments_by_url(video_url)
        if segments:
            for start_time, text in segments:
                print(f"{start_time}: {text}")
        else:
            print("Видео не найдено в базе данных.")

    def run(self):
        while True:
            choice = input("Введите '1' для добавления видео или '2' для запроса сегментов: ")
            if choice == '1':
                video_url = input("Введите URL видео на YouTube: ")
                self.add_video(video_url)
            elif choice == '2':
                video_url = input("Введите URL видео для запроса сегментов: ")
                self.query_segments(video_url)
            else:
                print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    app = VideoTranscriptApp()
    app.run()
