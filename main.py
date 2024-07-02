from database import VideoTranscriptDB, VideoTranscriptQuery
from parser import TranscriptParser
from multilingual_vectorizer import MultilingualVectorizer
from ollama_model import OllamaModel

class VideoTranscriptApp:
    def __init__(self):
        self.db = VideoTranscriptDB()
        self.query = VideoTranscriptQuery()
        self.parser = TranscriptParser()
        self.vectorizer = MultilingualVectorizer("intfloat/multilingual-e5-base")
        self.ollama_model = OllamaModel()

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
            self.db.insert_segment(video_id, start_time, text, video_url)
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
        distances, indices = self.vectorizer.search_similar(query_text, k=5)  # Ищем 5 ближайших сегментов

        print(f"Похожие сегменты на '{query_text}':")
        similar_segments = []
        for dist, idx in zip(distances, indices):
            segment = segments[idx] if idx < len(segments) else "<Сегмент не найден>"
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT start_time, url FROM segments WHERE text = ?", (segment,))
            result = cursor.fetchone()
            if result:
                start_time, url = result
                similar_segments.append((segment, start_time, url))

        self.generate_answers_for_segments(similar_segments, query_text)

    def generate_answers_for_segments(self, similar_segments, query_text):
        for segment, start_time, url in similar_segments:
            response = self.ollama_model.generate_answer_from_segment(segment, query_text)
            print(f"URL: {url}\nВремя начала: {start_time}\nОтвет: {response}\n")



    def generate_answer(self, query_text):
        segments = self.db.get_all_segments()
        self.vectorizer.build_index(segments)
        distances, indices = self.vectorizer.search_similar(query_text, k=1)

        closest_segment = segments[indices[0]]

        response = self.ollama_model.generate_response(closest_segment, query_text)
        return response

    def run(self):
        while True:
            choice = input(
                "Введите '1' для добавления видео, '2' для запроса сегментов, '3' для поиска по смыслу, '4' для генерации ответа")
            if choice == '1':
                video_url = input("Введите URL видео на YouTube: ")
                self.add_video(video_url)
            elif choice == '2':
                video_url = input("Введите URL видео для запроса сегментов: ")
                self.query_segments(video_url)
            elif choice == '3':
                query_text = input("Введите текст для поиска схожих сегментов: ")
                self.find_similar_segments(query_text)
            elif choice == '4':
                query_text = input("Введите текст для поиска и генерации ответа: ")
                response = self.generate_answer(query_text)
                print(f"Ответ: {response}")
            else:
                print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    app = VideoTranscriptApp()
    app.run()
