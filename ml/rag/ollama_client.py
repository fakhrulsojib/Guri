import os
import requests
import structlog
import time

logger = structlog.get_logger()

class OllamaClient:
    def __init__(self, host=None, port=None):
        self.host = host or os.getenv("OLLAMA_HOST", "ollama")
        self.port = port or os.getenv("OLLAMA_PORT", "11434")
        self.base_url = f"http://{self.host}:{self.port}"
        self.model = "tinyllama"  # Default for dev

    def is_alive(self):
        try:
            response = requests.get(f"{self.base_url}/")
            return response.status_code == 200
        except Exception:
            return False

    def ensure_model(self):
        """Check if model exists, pull if not"""
        try:
            # List models
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = [m['name'] for m in response.json().get('models', [])]
                # Check for tinyllama or tinyllama:latest
                if any(self.model in m for m in models):
                    logger.info(f"Model {self.model} is ready")
                    return True
            
            logger.info(f"Pulling model {self.model}...")
            # Pull model
            response = requests.post(f"{self.base_url}/api/pull", json={"name": self.model}, stream=True)
            for line in response.iter_lines():
                if line:
                    logger.debug(f"Pulling: {line.decode('utf-8')}")
            
            logger.info(f"Model {self.model} pulled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure model: {str(e)}")
            return False

    def generate(self, prompt, context=None):
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if context:
                payload["context"] = context
                
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Generate failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Ollama generation error: {str(e)}")
            return None
