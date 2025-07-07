"""
OpenAI Client Module
Handles conversational LLM responses using OpenAI API
"""

import openai
from config import Config

class OpenAIClient:
    def __init__(self):
        # Validate API key before initializing client
        if not Config.OPENAI_API_KEY or Config.OPENAI_API_KEY.strip() == "":
            raise ValueError("OpenAI API key is missing or empty. Please set OPENAI_API_KEY in your environment variables.")
        
        if not Config.OPENAI_API_KEY.startswith("sk-"):
            raise ValueError("OpenAI API key appears to be invalid. It should start with 'sk-'")
        
        print(f"🔑 OpenAI API key configured: {Config.OPENAI_API_KEY[:10]}...")
        
        try:
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            print("✅ OpenAI client initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize OpenAI client: {e}")
            raise
        
        self.history = []  # List of (role, content) tuples

    def ask(self, prompt: str, system_prompt: str = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            for role, content in self.history:
                messages.append({"role": role, "content": content})
            messages.append({"role": "user", "content": prompt})
            
            print(f"🤖 Sending request to OpenAI with {len(messages)} messages")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            
            answer = response.choices[0].message.content.strip()
            print(f"🤖 Received response from OpenAI: {answer[:100]}...")
            
            self.history.append(("user", prompt))
            self.history.append(("assistant", answer))
            return answer
            
        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            # Return a fallback response instead of crashing
            fallback_response = "I'm sorry, I'm having trouble connecting to my AI service right now. Please try again in a moment."
            print(f"🤖 Using fallback response: {fallback_response}")
            return fallback_response

    def reset_history(self):
        self.history = [] 