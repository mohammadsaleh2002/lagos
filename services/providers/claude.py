import anthropic

from services.ai_provider import AIProvider, ProviderRegistry, extract_json_from_text


@ProviderRegistry.register
class ClaudeProvider(AIProvider):
    name = 'claude'

    def generate(self, api_key, prompt, system_prompt=''):
        client = anthropic.Anthropic(api_key=api_key)
        kwargs = {
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 8000,
            'messages': [{'role': 'user', 'content': prompt}],
        }
        if system_prompt:
            kwargs['system'] = system_prompt

        response = client.messages.create(**kwargs)
        return response.content[0].text

    def generate_json(self, api_key, prompt, system_prompt=''):
        text = self.generate(api_key, prompt, system_prompt)
        return extract_json_from_text(text)
