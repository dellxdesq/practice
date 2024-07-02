from transformers import AutoTokenizer, AutoModel
import torch
import faiss

class MultilingualVectorizer:
    def __init__(self, model_name, index_filename="vector_index.faiss"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.index_filename = index_filename
        self.index = None

    '''Токенизирует входной текст и преобразует его в тензоры.
Пропускает токенизированный текст через модель без вычисления градиентов (используя torch.no_grad()).
Получает эмбеддинги из последнего скрытого слоя модели и усредняет их по размерности.
Возвращает эмбеддинги в виде списка.'''
    def get_embeddings(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embeddings.tolist()

    '''Создает индекс FAISS для заданного списка текстов.
Получает эмбеддинги для каждого текста и сохраняет их в список vectors.
Преобразует список векторов в формат numpy.
Создает индекс FAISS типа IndexFlatL2 (для поиска с использованием L2 расстояния) и добавляет в него векторы.
Сохраняет созданный индекс в файл с именем index_filename.'''
    def build_index(self, texts):
        vectors = []
        for text in texts:
            vector = self.get_embeddings(text)
            vectors.append(vector)

        numpy_vectors = torch.tensor(vectors).numpy()
        self.index = faiss.IndexFlatL2(numpy_vectors.shape[1])
        self.index.add(numpy_vectors)

        faiss.write_index(self.index, self.index_filename)

    '''Загружает индекс FAISS из файла.'''
    def load_index(self):
        self.index = faiss.read_index(self.index_filename)

    '''Проверяет, построен ли индекс или загружен.
Получает эмбеддинг для текстового запроса.
Преобразует эмбеддинг в формат numpy.
Выполняет поиск в индексе FAISS, возвращая k самых близких векторов (сегментов).
Возвращает расстояния и индексы найденных векторов.'''
    def search_similar(self, query_text, k=5):
        if self.index is None:
            raise RuntimeError("Index is not built or loaded. Call build_index() or load_index() first.")

        query_vector = self.get_embeddings(query_text)
        query_vector = torch.tensor(query_vector).numpy()

        distances, indices = self.index.search(query_vector.reshape(1, -1), k)
        return distances[0], indices[0]
