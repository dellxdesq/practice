from database import VideoTranscriptDB, VideoTranscriptQuery
from parser import TranscriptParser
from multilingual_vectorizer import MultilingualVectorizer

class VideoTranscriptApp:
    def __init__(self):
        self.db = VideoTranscriptDB()
        self.query = VideoTranscriptQuery()
        self.parser = TranscriptParser()
        self.vectorizer = MultilingualVectorizer("intfloat/multilingual-e5-base")

    def add_video(self, video_url):
        transcript = self.parser.get_transcript(video_url)
        if not transcript:
            print("Расшифровка на русском языке недоступна для данного видео.")
            return

        video_id = self.db.insert_video(video_url)
        if video_id is None:
            print("Это видео уже есть в базе данных.")
            return

        merged_transcript = self.parser.merge_transcripts(transcript)
        for entry in merged_transcript:
            start_time = self.parser.format_time(entry['start'])
            text = entry['text']
            self.db.insert_segment(video_id, start_time, text)
            print(f"{start_time}: {text}")

    def query_segments(self, video_url):
        segments = self.query.get_segments_by_url(video_url)
        if segments:
            for start_time, text in segments:
                print(f"{start_time}: {text}")
        else:
            print("Видео не найдено в базе данных.")

    def find_similar_segments(self, query_text):
        segments = self.db.get_all_segments()
        self.vectorizer.build_index(segments)
        distances, indices = self.vectorizer.search_similar(query_text)

        print(f"Похожие сегменты на '{query_text}':")
        for dist, idx in zip(distances, indices):
            segment = segments[idx] if idx < len(segments) else "<Сегмент не найден>"
            print(f"Расстояние: {dist}, Индекс сегмента: {idx}, Сегмент текста: {segment}")

    def run(self):
        while True:
            choice = input("Введите '1' для добавления видео, '2' для запроса сегментов, '3' для поиска по смыслу: ")
            if choice == '1':
                video_url = input("Введите URL видео на YouTube: ")
                self.add_video(video_url)
            elif choice == '2':
                video_url = input("Введите URL видео для запроса сегментов: ")
                self.query_segments(video_url)
            elif choice == '3':
                query_text = input("Введите текст для поиска схожих сегментов: ")
                self.find_similar_segments(query_text)
            else:
                print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    app = VideoTranscriptApp()
    app.run()
