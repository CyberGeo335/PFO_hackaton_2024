# back/routes.py

from fastapi import APIRouter, Request
from pydantic import BaseModel
from utils.knowledge_base import create_knowledge_base
from utils.response import response
from utils.query_processing import reranker
from transformers import AutoTokenizer
from vllm import LLM
import torch

main_router = APIRouter()

# Создание базы знаний при инициализации
knowledge_base_retriever = create_knowledge_base('/home/user1/GreenQuery/datasets/knowledge_data_del/')
tokenizer = AutoTokenizer.from_pretrained("/home/user1/GreenQuery/llm_saiga_src")
llm = LLM(
    model="/home/user1/GreenQuery/llm_saiga_src",
    dtype=torch.float16,
    gpu_memory_utilization=0.65,
    max_seq_len_to_capture=8192
)


class QueryRequest(BaseModel):
    query: str
    prj_dir: str = None

@main_router.post("/query")
async def handle_query(request: QueryRequest):
    query = request.query
    prj_dir = '/home/user1/GreenQuery/datasets/knowledge_data_del/' if 'база знаний' in query.lower() else request.prj_dir
    answer = response(query, prj_dir, knowledge_base_retriever, reranker, tokenizer, llm)
    return {"answer": answer}
