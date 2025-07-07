"""
OpenAI Client Module
Handles conversational LLM responses using OpenAI API
"""

import openai
from config import Config

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        self.history = []  # List of (role, content) tuples

    def ask(self, prompt: str, system_prompt: str = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for role, content in self.history:
            messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        answer = response.choices[0].message.content.strip()
        self.history.append(("user", prompt))
        self.history.append(("assistant", answer))
        return answer

    def reset_history(self):
        self.history = [] 