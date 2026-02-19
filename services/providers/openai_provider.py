from openai import OpenAI

from services.ai_provider import AIProvider, ProviderRegistry, extract_json_from_text


@ProviderRegistry.register
class OpenAIProvider(AIProvider):
    name = 'openai'

    def generate(self, api_key, prompt, system_prompt=''):
        client = OpenAI(api_key=api_key)
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=8000,
        )
        return response.choices[0].message.content

    def generate_json(self, api_key, prompt, system_prompt=''):
        text = self.generate(api_key, prompt, system_prompt)
        return extract_json_from_text(text)
