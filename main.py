from transcript_database import VideoTranscriptDB, VideoTranscriptQuery
from transcript_parser import TranscriptParser
from multilingual_vectorizer import MultilingualVectorizer
from ollama_model import OllamaModel

class VideoTranscriptApp:
    def __init__(self):
        self.db = VideoTranscriptDB()
        self.query = VideoTranscriptQuery()
        self.parser = TranscriptParser()
        self.vectorizer = MultilingualVectorizer("intfloat/multilingual-e5-base")

    def add_video(self, video_url):
        transcript = self.parser.get_transcript(video_url)
        if not transcript:
            print("Расшифровка недоступна.")
            return

        video_id = self.db.insert_video(video_url)
        if video_id is None:
            print("Это видео уже добавлено.")
            return

        print("Выберите максимальную длительность объединения (в секундах):")
        print("1. 5 секунд")
        print("2. 15 секунд")
        print("3. 30 секунд")
        choice = input("Введите номер выбора: ")

        if choice == '1':
            max_duration = 5.0
        elif choice == '2':
            max_duration = 15.0
        elif choice == '3':
            max_duration = 30.0
        else:
            print("Неверный выбор. Используется значение по умолчанию: 60 секунд.")
            max_duration = 60.0

        merged_transcript = self.parser.merge_transcripts(transcript, max_duration=max_duration)
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

        # Выбор модели Ollama
        model_name = self.choose_ollama_model()
        ollama_model = OllamaModel(model_name)

        for dist, idx in zip(distances, indices):
            segment = segments[idx] if idx < len(segments) else "<Сегмент не найден>"
            cursor = self.db.conn.cursor()
            cursor.execute("SELECT start_time, url FROM segments WHERE text = ?", (segment,))
            result = cursor.fetchone()
            if result:
                start_time, url = result
                similar_segments.append((segment, start_time, url))

        # Вывод промежуточной строки со всеми изначальными сегментами
        print("Промежуточные сегменты:")
        for segment, start_time, url in similar_segments:
            print(f"{url} на таймкоде {start_time} с сегментом '{segment}'")

        # Генерация краткого содержания для каждого сегмента
        summarized_segments = []
        for segment, start_time, url in similar_segments:
            summary = ollama_model.summarize_segment(segment)
            summarized_segments.append((summary, start_time, url))

        for summary, start_time, url in summarized_segments:
            print(f"По вашему запросу было найдено: {url} на таймкоде {start_time} с кратким содержанием '{summary}'")

    def generate_answer(self, query_text):
        segments = self.db.get_all_segments()
        self.vectorizer.build_index(segments)
        distances, indices = self.vectorizer.search_similar(query_text, k=5)

        closest_segments = [segments[idx] for idx in indices]
        for el in closest_segments:
            print(el)
        # Выбор модели Ollama
        model_name = self.choose_ollama_model()
        ollama_model = OllamaModel(model_name)

        # Ранжирование сегментов по полезности
        ranked_segment = ollama_model.rank_segments(closest_segments, query_text)

        cursor = self.db.conn.cursor()
        cursor.execute("SELECT start_time, url FROM segments WHERE text = ?", (ranked_segment,))
        result = cursor.fetchone()
        if result:
            start_time, url = result
            print(f"Наиболее полезный сегмент: {start_time} - {ranked_segment} (URL: {url})")

        response = ollama_model.generate_ranked_response(ranked_segment, query_text)
        print(f"Ответ на основе сегмента {ranked_segment}")
        return response

    def choose_ollama_model(self):
        print("Выберите языковую модель Ollama:")
        print("1. llama3")
        print("2. ilyagusev/saiga_llama3")
        choice = input("Введите номер выбора: ")

        if choice == '1':
            return 'llama3'
        elif choice == '2':
            return 'ilyagusev/saiga_llama3'
        else:
            print("Неверный выбор. Перезапустите программу")
            return 'model_a'

    def run(self):
        while True:
            choice = input(
                "Введите '1' для добавления видео, '2' для запроса сегментов, '3' для поиска нужного видео, '4' для ввода вопроса: ")
            if choice == '1':
                video_url = input("Введите URL видео на YouTube: ")
                self.add_video(video_url)
            elif choice == '2':
                video_url = input("Введите URL видео для запроса сегментов: ")
                self.query_segments(video_url)
            elif choice == '3':
                query_text = input("Введите текст для поиска нужного видео: ")
                self.find_similar_segments(query_text)
            elif choice == '4':
                query_text = input("Введите ваш вопрос: ")
                response = self.generate_answer(query_text)
                print(f"Ответ: {response}")
            else:
                print("Неверный ввод. Попробуйте снова.")

if __name__ == "__main__":
    app = VideoTranscriptApp()
    app.run()
