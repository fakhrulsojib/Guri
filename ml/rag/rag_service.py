import structlog
import chromadb
from typing import List, Dict, Optional
import os
import json

from .ollama_client import OllamaClient
from .embedding_generator import EmbeddingGenerator
from .chunk_manager import ChunkManager

logger = structlog.get_logger()

class RAGService:
    def __init__(self):
        self.chroma_host = os.getenv("CHROMA_HOST", "chromadb_server")
        self.chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        
        self.chroma_client = chromadb.HttpClient(
            host=self.chroma_host,
            port=self.chroma_port
        )
        
        self.collection_name = "log_analytics"
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        self.ollama = OllamaClient()
        self.embedder = EmbeddingGenerator()
        self.chunker = ChunkManager()

    def ingest_logs(self, logs: List[Dict]) -> int:
        """
        Process raw logs, cluster them, generate embeddings, and store in Chroma.
        Returns number of chunks created.
        """
        if not logs:
            return 0

        # Group logs into chunks
        chunks = self.chunker.cluster_logs(logs)
        if not chunks:
            return 0
        
        chunk_ids = []
        chunk_texts = []
        chunk_metadatas = []
        
        for chunk in chunks:
            chunk_ids.append(chunk.id)
            chunk_texts.append(chunk.check_content)
            chunk_metadatas.append({
                "source_id": chunk.source_id,
                "log_level": chunk.log_level,
                "start_time": chunk.start_time,
                "end_time": chunk.end_time,
                "count": chunk.count,
                "template": chunk.template
            })

        # Generate embeddings
        embeddings = self.embedder.generate_embeddings(chunk_texts)
        
        # Upsert to Chroma
        if embeddings:
            self.collection.upsert(
                ids=chunk_ids,
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=chunk_metadatas
            )
            logger.info(f"Ingested {len(chunks)} log chunks into RAG")
            
        return len(chunks)

    def query_logs(self, query_text: str, filters: Dict = None) -> Dict:
        """
        RAG Query Pipeline:
        1. Embed Query
        2. Retrieve Context
        3. Generate Answer
        """
        # 1. Embed and Search
        query_emb = self.embedder.generate_embedding(query_text)
        
        search_params = {
            "query_embeddings": [query_emb],
            "n_results": 10
        }
        
        if filters:
            # Simple metadata filtering if provided
            pass # TODO: Implement complex filter logic if needed
            
        results = self.collection.query(**search_params)
        
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        if not documents:
            return {
                "answer": "No relevant logs found for your query.",
                "context": []
            }

        # 2. Construct Context
        context_str = "\n---\n".join(documents)
        
        # 3. Generate with Ollama
        system_prompt = (
            "You are a Log Analytics AI. You have been provided with summaries of log groups (chunks) "
            "from a system. Each chunk represents multiple logs of the same pattern.\n"
            "Use the provided context to answer the user's question.\n"
            "If the answer isn't in the logs, say so.\n"
            "Focus on error patterns, timing, and sources."
        )
        
        final_prompt = f"{system_prompt}\n\nContext Logs:\n{context_str}\n\nUser Question: {query_text}"
        
        # Ensure model is ready (pull if needed)
        self.ollama.ensure_model()
        
        response = self.ollama.generate(prompt=final_prompt)
        answer = response.get("response", "Failed to generate response") if response else "Error communicating with LLM"

        return {
            "answer": answer,
            "context": metadatas # Return metadata as context reference
        }
