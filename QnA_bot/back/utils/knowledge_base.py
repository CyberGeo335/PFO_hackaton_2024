# app/utils/knowledge_base.py

from llama_index.core import VectorStoreIndex
from load_files import load_project_files


def create_knowledge_base(base_dir):
    docs = load_project_files(base_dir)
    if docs:
        index = VectorStoreIndex.from_documents(documents=docs, show_progress=True)
        retriever = index.as_retriever(similarity_top_k=7)
        return retriever
    return None
