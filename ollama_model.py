# ollama_model.py
import ollama

class OllamaModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def rank_segments(self, segments, query_text):
        message = f"""
        Учитывая следующие сегменты текста, выбери тот, который наиболее полезен для ответа на вопрос '{query_text}'.
        Ты должен выбрать один из сегментов, в котором находится более точная информация по заданному вопросу.
        Далее на основе этого сегмента сформулировать ответ.

        Сегменты:
        {'\n'.join([f'{i+1}. {segment}' for i, segment in enumerate(segments)])}

        Ответ:
        """
        response = ollama.chat(model=self.model_name, messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])
        ranked_segment = response['message']['content'].strip()
        return ranked_segment

    def generate_ranked_response(self, ranked_segment, query_text):
        return self.generate_response(ranked_segment, query_text)

    def generate_response(self, context, question):
        message = f"""
        Ты должен ответить на вопрос, используя только следующий контекст. Если ты не знаешь ответа на основе контекста, 
        скажи "Извините, я не знаю ответа на этот вопрос."

        Контекст: {context}

        Вопрос: {question}
        Ответ:
        """
        response = ollama.chat(model=self.model_name, messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])
        answer = response['message']['content']
        return answer