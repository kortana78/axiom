"""Free-LLM idea adapter.  Proposals only; never proof results."""
from .config import Provider, load_providers
from .client import LLMClient, LLMError, parse_json_text

__all__ = ["Provider", "load_providers", "LLMClient", "LLMError",
           "parse_json_text"]
