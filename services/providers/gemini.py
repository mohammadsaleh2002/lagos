import google.generativeai as genai

from services.ai_provider import AIProvider, ProviderRegistry, extract_json_from_text


@ProviderRegistry.register
class GeminiProvider(AIProvider):
    name = 'gemini'

    def generate(self, api_key, prompt, system_prompt=''):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            'gemini-2.0-flash',
            system_instruction=system_prompt or None
        )
        response = model.generate_content(prompt)
        return response.text

    def generate_json(self, api_key, prompt, system_prompt=''):
        text = self.generate(api_key, prompt, system_prompt)
        return extract_json_from_text(text)
