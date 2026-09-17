"""
Provider-Agnostic AI Service Interface.
Supports Gemini 3.6-flash, fallback models, secure key retrieval, zero log leakage.
"""
import os
import requests
import json
from typing import Dict, Any, Optional, List

class AIService:
    def __init__(self, api_key: Optional[str] = None, provider: str = "gemini"):
        self.provider = provider
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.candidate_models = ["gemini-3.5-flash-lite", "gemini-3.6-flash", "gemini-flash-latest", "gemini-3.7-flash"]

    def set_key(self, api_key: str):
        self.api_key = api_key.strip() if api_key else ""

    def get_masked_key(self) -> str:
        if not self.api_key:
            return "Not Configured"
        if len(self.api_key) <= 8:
            return "******"
        return f"{self.api_key[:4]}...{self.api_key[-4:]}"

    def has_valid_key(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    def generate_json(self, prompt: str, system_instruction: str = "", temperature: float = 0.7) -> Dict[str, Any]:
        """Generates structured JSON response from LLM."""
        if not self.has_valid_key():
            raise ValueError("Missing or invalid Gemini API Key. Please provide a key in the UI or environment.")

        clean_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with a valid, clean JSON object. Do not wrap in markdown quotes if possible or use ```json blocks."
        
        contents_parts = [{"text": clean_prompt}]
        payload: Dict[str, Any] = {
            "contents": [{"parts": contents_parts}],
            "generationConfig": {
                "temperature": temperature,
                "topP": 0.95,
                "maxOutputTokens": 3000
            }
        }
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

        last_error = ""
        for model in self.candidate_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                res = requests.post(url, json=payload, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    cands = data.get("candidates", [])
                    if cands and "content" in cands[0] and "parts" in cands[0]["content"]:
                        raw_text = cands[0]["content"]["parts"][0]["text"].strip()
                        # Clean markdown json wraps
                        if raw_text.startswith("```json"):
                            raw_text = raw_text[7:]
                        elif raw_text.startswith("```"):
                            raw_text = raw_text[3:]
                        if raw_text.endswith("```"):
                            raw_text = raw_text[:-3]
                        raw_text = raw_text.strip()
                        try:
                            return json.loads(raw_text)
                        except json.JSONDecodeError as je:
                            # Try greedy extraction between { and }
                            s = raw_text.find("{")
                            e = raw_text.rfind("}")
                            if s != -1 and e != -1 and e > s:
                                return json.loads(raw_text[s:e+1])
                            raise je
                else:
                    last_error = f"HTTP {res.status_code}: {res.text[:150]}"
            except Exception as ex:
                last_error = str(ex)
                continue

        raise RuntimeError(f"AI Generation Failed across candidate models. Details: {last_error}")
