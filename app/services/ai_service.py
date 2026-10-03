
import os
import requests
from config import Config

class AIServiceError(Exception):
    """Yapay zekâ servisine özel hata sınıfı."""
    pass

class AIService:
    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.model = "openai/gpt-oss-120b"
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def _get_system_prompt(self):
        return Config.BUSINESS_CONTEXT

    def yanit_uret(self, mesaj, gecmis=None):
        if gecmis is None:
            gecmis = []

        if not self.api_key or self.api_key.startswith("gsk_buraya"):
            return "Demo Modu: Groq API anahtarı ayarlanmadığı için bu otomatik demo yanıtıdır."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": self._get_system_prompt()}]
        messages.extend(gecmis)
        messages.append({"role": "user", "content": mesaj})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(self.url, json=payload, headers=headers, timeout=10)
            if response.status_code != 200:
                raise AIServiceError(f"Groq API hatası: {response.status_code} - {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.RequestException as e:
            raise AIServiceError(f"Bağlantı hatası oluştu: {str(e)}")

# Dosya sonunda tek bir örnek örnekleniyor
ai_service = AIService()