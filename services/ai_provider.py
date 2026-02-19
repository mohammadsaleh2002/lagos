import json
import logging
from abc import ABC, abstractmethod

from models.api_key import get_next_key, record_key_error, reset_key_errors

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base class for AI providers."""

    name = ''

    @abstractmethod
    def generate(self, api_key, prompt, system_prompt=''):
        """Generate text from prompt. Returns string response."""
        pass

    @abstractmethod
    def generate_json(self, api_key, prompt, system_prompt=''):
        """Generate and parse JSON response. Returns dict."""
        pass


class ProviderRegistry:
    """Registry for AI providers with key rotation."""

    _providers = {}

    @classmethod
    def register(cls, provider_class):
        cls._providers[provider_class.name] = provider_class()
        return provider_class

    @classmethod
    def get_provider(cls, name):
        return cls._providers.get(name)

    @classmethod
    def list_providers(cls):
        return list(cls._providers.keys())

    @classmethod
    def generate(cls, db, fernet, provider_name, prompt, system_prompt=''):
        """Generate text using a provider with automatic key rotation."""
        provider = cls.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        key_id, api_key = get_next_key(db, fernet, provider_name)
        if not api_key:
            raise RuntimeError(f"No active API keys for provider: {provider_name}")

        try:
            result = provider.generate(api_key, prompt, system_prompt)
            reset_key_errors(db, key_id)
            return result
        except Exception as e:
            logger.error(f"Provider {provider_name} key {key_id} failed: {e}")
            record_key_error(db, key_id)
            # Try one more key
            key_id2, api_key2 = get_next_key(db, fernet, provider_name)
            if api_key2 and key_id2 != key_id:
                try:
                    result = provider.generate(api_key2, prompt, system_prompt)
                    reset_key_errors(db, key_id2)
                    return result
                except Exception as e2:
                    logger.error(f"Provider {provider_name} key {key_id2} also failed: {e2}")
                    record_key_error(db, key_id2)
            raise

    @classmethod
    def generate_json(cls, db, fernet, provider_name, prompt, system_prompt=''):
        """Generate JSON using a provider with automatic key rotation."""
        provider = cls.get_provider(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        key_id, api_key = get_next_key(db, fernet, provider_name)
        if not api_key:
            raise RuntimeError(f"No active API keys for provider: {provider_name}")

        try:
            result = provider.generate_json(api_key, prompt, system_prompt)
            reset_key_errors(db, key_id)
            return result
        except Exception as e:
            logger.error(f"Provider {provider_name} key {key_id} failed: {e}")
            record_key_error(db, key_id)
            key_id2, api_key2 = get_next_key(db, fernet, provider_name)
            if api_key2 and key_id2 != key_id:
                try:
                    result = provider.generate_json(api_key2, prompt, system_prompt)
                    reset_key_errors(db, key_id2)
                    return result
                except Exception as e2:
                    logger.error(f"Provider {provider_name} key {key_id2} also failed: {e2}")
                    record_key_error(db, key_id2)
            raise


def find_active_provider(db, fernet):
    """Find the first provider that has active API keys."""
    for pname in ProviderRegistry.list_providers():
        key_id, api_key = get_next_key(db, fernet, pname)
        if api_key:
            return pname
    return None


def extract_json_from_text(text):
    """Try to extract JSON from text that may contain markdown code blocks."""
    text = text.strip()
    if text.startswith('```'):
        lines = text.split('\n')
        start = 1
        end = len(lines)
        for i in range(1, len(lines)):
            if lines[i].strip() == '```':
                end = i
                break
        text = '\n'.join(lines[start:end])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        brace_start = text.find('{')
        if brace_start >= 0:
            depth = 0
            for i in range(brace_start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[brace_start:i + 1])
                        except json.JSONDecodeError:
                            break
        raise
