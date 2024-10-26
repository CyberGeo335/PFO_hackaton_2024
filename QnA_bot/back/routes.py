# back/routes.py

from flask import Blueprint, request, jsonify
from app.utils.knowledge_base import create_knowledge_base
from app.utils.response import response
from app.utils.query_processing import reranker
from transformers import AutoTokenizer
from vllm import LLM

main_bp = Blueprint('main', __name__)

# Создание базы знаний при инициализации
knowledge_base_retriever = create_knowledge_base('/home/user1/GreenQuery/datasets/knowledge_data_del/')
tokenizer = AutoTokenizer.from_pretrained("/home/user1/GreenQuery/llm_saiga_src")
llm = LLM(
    model="/home/user1/GreenQuery/llm_saiga_src",
    dtype=torch.float16,
    gpu_memory_utilization=0.65,
    max_seq_len_to_capture=8192
)

@main_bp.route('/query', methods=['POST'])
def handle_query():
    data = request.json
    query = data.get('query')
    
    # Если директория проекта не указана, используем базу знаний
    if 'база знаний' in query.lower():
        prj_dir = '/home/user1/GreenQuery/datasets/knowledge_data_del/'
    else:
        prj_dir = data.get('prj_dir', None)
    
    answer = response(query, prj_dir, knowledge_base_retriever, reranker, tokenizer, llm)
    return jsonify({'answer': answer})

