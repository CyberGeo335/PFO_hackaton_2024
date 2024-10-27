# app/utils/query_processing.py

from sentence_transformers import CrossEncoder
import numpy as np

reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')

# Классификация запроса: суммаризация или вопрос
def classify_query(query):
    """
        Классифицирует запрос как запрос на суммаризацию или вопрос.

        Параметры:
            query (str): Запрос пользователя.

        Возвращает:
            str: Тип запроса — "summarization" или "question".
    """
    if "суммаризация" in query.lower() or "обзор" in query.lower():
        return "summarization"
    return "question"

# Функция для реранкинга топовых документов
def top_k_rerank(query: str, retriever, reranker, top_k: int = 2):
    """
        Ранжирует список документов на основе запроса, возвращая топ-k релевантных результатов.

        Параметры:
            query (str): Запрос пользователя.
            retriever (VectorStoreIndexRetriever): Объект для поиска по базе знаний или проекту.
            reranker (CrossEncoder): Модель для реранкинга.
            top_k (int): Количество лучших документов для возврата.

        Возвращает:
            tuple: Список названий документов, текстов и релевантного значения.
    """
    documents = retriever.retrieve(query)
    relevant_score = documents[0].score
    print(f'Наивысшее значение релевантности документов: {relevant_score}')

    candidate_texts = [x.text for x in documents]
    candidate_names = [x.metadata['название документа'] for x in documents]

    rerank_scores = reranker.predict(list(zip([query] * len(candidate_texts), candidate_texts)))
    ranked_indices = np.argsort(rerank_scores)[::-1]

    names = [candidate_names[i] for i in ranked_indices][:top_k]
    texts = [candidate_texts[i] for i in ranked_indices][:top_k]

    return names, texts, relevant_score
