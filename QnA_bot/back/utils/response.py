# app/utils/response.py

from transformers import pipeline
import torch
import pandas as pd
from llama_index.core import VectorStoreIndex
from query_processing import top_k_rerank, classify_query
from load_files import load_project_files
from llama_index.core.postprocessor import SimilarityPostprocessor
from vllm import LLM, SamplingParams

summarizer = pipeline("summarization", model="IlyaGusev/rut5_base_sum_gazeta")

# Функция для суммаризации документов
def summarize_documents(docs, max_length=150):
    """
        Создает суммаризацию для текста из списка документов.

        Параметры:
            docs (list): Список объектов Document с текстом.
            max_length (int): Максимальная длина суммаризации.

        Возвращает:
            str: Краткая суммаризация текста из документов.
    """
    full_text = ' '.join([doc.text for doc in docs])
    summary = summarizer(full_text, max_length=max_length, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def get_example_prompts(num_examples=3):
    """
        Загружает случайные примеры запросов и ответов из CSV файла.

        Параметры:
            num_examples (int): Количество примеров для генерации.

        Возвращает:
            str: Строка с примерами вопросов и ответов.
    """
    answer_csv_path = '/home/user1/GreenQuery/datasets/metrics/train.csv'
    answer_data = pd.read_csv(answer_csv_path, sep='\t')
    examples = answer_data.sample(n=num_examples)  # Берем случайные примеры
    example_text = ""
    for _, row in examples.iterrows():
        question = row['Вопрос']
        answer = row['Ответ']
        example_text += f"Вопрос: {question}\nОтвет: {answer}\n\n"
    return example_text


def vllm_infer(tokenizer,
               wrapped_llm,
               texts, query,
               temperature: float = 0.1,
               top_p: float = 0.95,
               top_k: int = 50,
               max_tokens: int = 1024,
               repetition_penalty: float = 1.05,
               presence_penalty: float = 0.5,
               frequency_penalty: float = 0.2,
               stop=["Я не могу ответить на ваш вопрос.", "Ответ окончен"]):
    """
        Формирует ответ на основе контекста и примеров с использованием LLM-saiga_8b.

        - SYSTEM_PROMPT - глобальный промпт для настройки
        - user_prompt - промпт для пользовательских запросов, с подкреплением примеров из train.csv
        и конкретизации того, что результат должен быть связан с экологией.

        Параметры:
            tokenizer (AutoTokenizer): Токенайзер для модели.
            wrapped_llm (LLM): Модель большой языковой модели.
            texts (str): Контекст, на основе которого строится ответ.
            query (str): Запрос пользователя.
            temperature (float): Температура для управления случайностью генерации.
            top_p (float): Порог вероятности для сэмплирования токенов.
            top_k (int): Количество наилучших токенов для выбора на каждом шаге.
            max_tokens (int): Максимальное количество токенов в ответе.
            repetition_penalty (float): Штраф за повторение токенов.
            presence_penalty (float): Штраф за присутствие определенных токенов.
            frequency_penalty (float): Штраф за частоту использования токенов.
            stop (list): Список стоп-токенов.

        Возвращает:
            list: Список ответов на запросы пользователя.
    """

    SYSTEM_PROMPT = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."

    example_prompts = get_example_prompts(num_examples=3)

    user_prompt = '''Ниже приведены примеры вопросов и ответов. Постарайся придерживаться их структуры и уровня детализации.
        {examples}

        Используй только следующий контекст, чтобы подробно ответить на вопрос в конце.
        Пожалуйста, укажи все важные детали, присутствующие в контексте.
        Если контекст не соотносится с вопросом, скажи, что ты не можешь ответить на данный вопрос.
        Если вопрос не относится к экологической тематике, выведи фразу "Я не могу ответить на ваш вопрос." и не выводи ничего больше.

        Контекст:
        =========== 
        {texts} 
        =========== 

        Вопрос:
        =========== 
        {query}'''.format(examples=example_prompts, texts=texts, query=query)

    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        max_tokens=max_tokens,
        repetition_penalty=repetition_penalty,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        stop=stop
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    prompt = wrapped_llm.llm_engine.tokenizer.tokenizer.apply_chat_template(
        conversation=messages, add_generation_prompt=True, tokenize=False
    )
    prompts = [prompt]
    outputs = wrapped_llm.generate(prompts, sampling_params)

    answers = [output.outputs[0].text for output in outputs]
    torch.cuda.empty_cache()
    return answers


# Функция для генерации ответа с проверкой на релевантность
def response(query,
             prj_dir,
             knowledge_retriever,
             reranker,
             tokenizer,
             llm):
    """
        Обрабатывает запрос: определяет его тип (суммаризация или вопрос),
        извлекает соответствующие документы из базы знаний или загруженного проекта, и генерирует ответ.

        Параметры:
            query (str): Запрос пользователя.
            prj_dir (str): Путь к директории загруженного проекта.
            knowledge_retriever (VectorStoreIndexRetriever): Объект для поиска по базе знаний.
            reranker (CrossEncoder): Модель для реранкинга.
            tokenizer (AutoTokenizer): Токенайзер для модели.
            llm (LLM): Модель LLM для генерации текста.

        Возвращает:
            str: Ответ на запрос пользователя или сообщение о его отсутствии.
    """

    query_type = classify_query(query)

    # Если запрос на суммаризацию загруженного проекта
    if query_type == "summarization":
        docs = load_project_files(prj_dir)
        return summarize_documents(docs)

    # Если запрос относится к базе знаний
    elif "база знаний" in query.lower():
        names, chunks, relevant_score = top_k_rerank(query, knowledge_retriever, reranker)
        if relevant_score >= 0.5:
            answer = vllm_infer(tokenizer, llm, ' '.join(chunks), query)
            return answer[0] if answer[0] != 'Я не могу ответить на ваш вопрос.' else "Нет подходящего ответа."
        else:
            return 'Запрос не найден в базе знаний.'

    # Если запрос касается загруженного проекта
    else:
        docs = load_project_files(prj_dir)
        prj_index = VectorStoreIndex.from_documents(documents=docs, show_progress=True)
        prj_retriever = prj_index.as_retriever(similarity_top_k=7,
                                               node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.85)])
        names, chunks, relevant_score = top_k_rerank(query, prj_retriever, reranker)
        if relevant_score >= 0.5:
            answer = vllm_infer(tokenizer, llm, ' '.join(chunks), query)
            return answer[0] if answer[0] != 'Я не могу ответить на ваш вопрос.' else "Нет подходящего ответа."
        else:
            return 'Запрос не найден в загруженном проекте.'