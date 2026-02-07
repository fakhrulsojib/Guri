from ml.rag.ollama_client import OllamaClient
import time
import os

print("Starting RAG Module Test...")

# Check Ollama Connection
client = OllamaClient(port=os.getenv("OLLAMA_PORT", "11435"))
if client.is_alive():
    print("✅ Ollama Service is Reachable")
else:
    print("❌ Ollama Service Unreachable")
    exit(1)

# Check Model Availability
if client.ensure_model():
    print("✅ TinyLlama Model is Available")
else:
    print("❌ Failed to verify TinyLlama Model")
    exit(1)

print("Test Complete.")
