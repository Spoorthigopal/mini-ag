import requests
from typing import List
from app.config import settings
from app.shared.exceptions import EmbeddingServiceError
import logging

logger = logging.getLogger(__name__)

# Constants
NVIDIA_NIM_ENDPOINT: str = "https://integrate.api.nvidia.com/v1"
MODEL_NAME: str = "nvidia/nv-embed-v2"
VECTOR_DIMENSION: int = 1024

def embed_text(text: str) -> List[float]:
    """Generate embedding vector for text using NVIDIA NIM (1024-dimension)."""
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")
        
    api_key = settings.NVIDIA_API_KEY or settings.nvidia_nim_api_key
    if not api_key:
        raise EmbeddingServiceError("NVIDIA API key not set")

    url = f"{NVIDIA_NIM_ENDPOINT}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "input": text,
        "encoding_format": "float"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.ConnectionError as e:
        logger.error(f"NVIDIA NIM connection failed: {e}")
        raise EmbeddingServiceError(f"Connection failed: {str(e)}")
    except requests.Timeout as e:
        logger.error(f"NVIDIA NIM timeout: {e}")
        raise EmbeddingServiceError(f"Request timeout: {str(e)}")
    except Exception as e:
        logger.error(f"NVIDIA NIM request failed: {e}")
        raise EmbeddingServiceError(f"Request failed: {str(e)}")

    if response.status_code != 200:
        logger.error(f"NVIDIA NIM returned status code {response.status_code}: {response.text}")
        raise EmbeddingServiceError(f"NVIDIA NIM error ({response.status_code}): {response.text}")

    try:
        data = response.json()
        vector = data["data"][0]["embedding"]
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"Failed to parse NVIDIA NIM response: {e}. Content: {response.text}")
        raise EmbeddingServiceError("Invalid response format from embedding service")

    if len(vector) != VECTOR_DIMENSION:
        logger.error(f"Expected embedding dimension {VECTOR_DIMENSION}, got {len(vector)}")
        raise EmbeddingServiceError(f"Invalid embedding dimension returned: expected {VECTOR_DIMENSION}, got {len(vector)}")

    return vector

def embed_texts_batch(texts: List[str]) -> List[List[float]]:
    """Embed multiple texts efficiently by calling embed_text for each."""
    if not texts:
        raise ValueError("Texts list cannot be empty")
        
    vectors = []
    for i, text in enumerate(texts):
        try:
            vector = embed_text(text)
            vectors.append(vector)
        except Exception as e:
            logger.warning(f"Failed to embed text at index {i}: {e}")
            # skip failed, log warning
            continue
            
    return vectors

def get_embedding_dimension() -> int:
    """Return embedding dimension (1024)."""
    return VECTOR_DIMENSION


class NVIDIAEmbeddingsClient:
    """NVIDIA NIM Embeddings Client (Legacy compatibility wrapper)."""

    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY or settings.nvidia_nim_api_key
        self.base_url = NVIDIA_NIM_ENDPOINT
        self.model = MODEL_NAME
        self.embedding_dimension = VECTOR_DIMENSION

    def embed_text(self, text: str) -> List[float]:
        return embed_text(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return embed_texts_batch(texts)


# Global instance for legacy imports
embeddings_client = NVIDIAEmbeddingsClient()

def get_embeddings_client() -> NVIDIAEmbeddingsClient:
    return embeddings_client
