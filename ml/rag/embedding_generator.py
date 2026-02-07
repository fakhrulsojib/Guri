from sentence_transformers import SentenceTransformer
import os
import structlog

logger = structlog.get_logger()

class EmbeddingGenerator:
    def __init__(self, model_name='all-mpnet-base-v2'):
        self.model_name = model_name
        self.cache_folder = os.getenv("MODEL_CACHE_PATH", "/app/models")
        self.model = None

    def load_model(self):
        if self.model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            try:
                self.model = SentenceTransformer(self.model_name, cache_folder=self.cache_folder)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                raise

    def generate_embedding(self, text):
        if self.model is None:
            self.load_model()
        
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return []

    def generate_embeddings(self, texts):
        if self.model is None:
            self.load_model()
        
        try:
            return self.model.encode(texts).tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            return []
