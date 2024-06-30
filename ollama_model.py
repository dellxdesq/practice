import ollama
from database import VideoTranscriptDB
from multilingual_vectorizer import MultilingualVectorizer


class OllamaModel:
    def __init__(self):
        self.db = VideoTranscriptDB()
        self.vectorizer = MultilingualVectorizer("intfloat/multilingual-e5-base")

    def generate_response(self, query_text):
        segments = self.db.get_all_segments()
        self.vectorizer.build_index(segments)
        distances, indices = self.vectorizer.search_similar(query_text)

        matched_segments = []
        for dist, idx in zip(distances, indices):
            segment = segments[idx] if idx < len(segments) else "<Сегмент не найден>"
            matched_segments.append(segment)

        if not matched_segments:
            return "Извините, я не могу найти релевантную информацию в базе данных."

        response_text = " ".join(matched_segments)

        response = ollama.chat(model='ilyagusev/saiga_llama3', messages=[
            {
                'role': 'user',
                'content': response_text
            },
        ])

        response_content = response['message']['content']

        if response_content.strip() == "" or "не могу найти" in response_content.lower():
            return "Извините, я не могу найти релевантную информацию в базе данных."

        return response_content
