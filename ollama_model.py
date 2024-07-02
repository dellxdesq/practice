import ollama

class OllamaModel:
    def generate_response(self, context, question):
        # Формируем сообщение для модели, добавляя контекст и инструкцию для ответа только на основе контекста
        message = f"""
        Ты должен ответить на вопрос, используя только следующий контекст. Если ты не знаешь ответа на основе контекста, скажи "Извините, я не знаю ответа на этот вопрос."

        Контекст: {context}

        Вопрос: {question}
        Ответ:
        """
        # Отправляем запрос модели
        response = ollama.chat(model='llama3', messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])
        # Получаем ответ от модели
        answer = response['message']['content']
        return answer

    def generate_answer_from_segment(self, segment, query_text):
        # Формируем сообщение для модели, добавляя контекст и инструкцию для ответа только на основе контекста
        message = f"""
        Ты должен ответить на вопрос, используя только следующий контекст. Если ты не знаешь ответа на основе контекста, скажи "Извините, я не знаю ответа на этот вопрос."

        Контекст: {segment}

        Вопрос: {query_text}
        Ответ:
        """
        # Отправляем запрос модели
        response = ollama.chat(model='ilyagusev/saiga_llama3', messages=[
            {
                'role': 'user',
                'content': message,
            },
        ])
        # Получаем ответ от модели
        answer = response['message']['content']
        return answer
