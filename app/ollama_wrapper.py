import ollama
import asyncio
from typing import List, Dict, Any
import re

class ChatOllama:
    def __init__(self, api_base, model, max_retries=20):
        self.api_base = api_base
        self.model = model
        self.max_retries = max_retries
    
    async def achat(self, messages, **kwargs):
        try:
            response = ollama.chat(model=self.model, messages=messages)
            content = response['message']['content']
            
            # Check if the query is in Hebrew
            if self.is_hebrew(messages[-1]['content']):
                # If the response is not in Hebrew, translate it
                if not self.is_hebrew(content):
                    content = self.translate_to_hebrew(content)
            
            return content
        except Exception as e:
            print(f"Error in Ollama chat: {e}")
            return ""
    
    async def agenerate(self, messages: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        try:
            response = ollama.chat(model=self.model, messages=messages)
            content = response['message']['content']
            
            # Check if the query is in Hebrew
            if self.is_hebrew(messages[-1]['content']):
                # If the response is not in Hebrew, translate it
                if not self.is_hebrew(content):
                    content = self.translate_to_hebrew(content)
            
            return {
                    "choices": [
                            {
                                    "message": {
                                            "content": content,
                                            "role": "assistant"
                                    }
                            }
                    ]
            }
        except Exception as e:
            print(f"Error in Ollama generate: {e}")
            return {"choices": [{"message": {"content": "", "role": "assistant"}}]}
    
    def is_hebrew(self, text):
        # Simple check for Hebrew characters
        hebrew_pattern = re.compile(r'[\u0590-\u05FF\uFB1D-\uFB4F]')
        return bool(hebrew_pattern.search(text))
    
    def translate_to_hebrew(self, text):
        # Implement translation to Hebrew here
        # This is a placeholder - you'll need to use a translation service or library
        print("Translation to Hebrew needed")
        return text  # Return original text for now

class OllamaEmbedding:
    def __init__(self, api_base, model, max_retries=20):
        self.api_base = api_base
        self.model = model
        self.max_retries = max_retries
    
    def embed(self, text: str) -> List[float]:
        try:
            response = ollama.embeddings(model=self.model, prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"Error in Ollama embedding: {e}")
            return []
    
    async def aembed(self, text: str) -> List[float]:
        return await asyncio.to_thread(self.embed, text)
    
    async def aembed_many(self, texts: List[str]) -> List[List[float]]:
        return [await self.aembed(text) for text in texts]