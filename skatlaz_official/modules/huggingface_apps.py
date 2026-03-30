"""
Hugging Face Apps Module - Integration with various Hugging Face models
"""

import requests
import json
from typing import Optional, Dict, Any, List
from .utils import logger, load_config

class HuggingFaceApps:
    """Integration with Hugging Face models and apps"""
    
    def __init__(self):
        self.config = load_config()
        self.api_key = self.config.get("huggingface_api_key", "")
        self.models = {
            "text_generation": [
                "mistralai/Mistral-7B-Instruct-v0.1",
                "google/flan-t5-large",
                "meta-llama/Llama-2-7b-chat-hf"
            ],
            "image_generation": [
                "stabilityai/stable-diffusion-2-1",
                "runwayml/stable-diffusion-v1-5",
                "black-forest-labs/FLUX.1-dev"
            ],
            "image_to_text": [
                "Salesforce/blip-image-captioning-large",
                "nlpconnect/vit-gpt2-image-captioning"
            ],
            "translation": [
                "facebook/m2m100_418M",
                "Helsinki-NLP/opus-mt-en-es"
            ],
            "summarization": [
                "facebook/bart-large-cnn",
                "t5-large"
            ],
            "question_answering": [
                "deepset/roberta-base-squad2",
                "distilbert-base-cased-distilled-squad"
            ],
            "text_to_speech": [
                "facebook/fastspeech2-en-ljspeech",
                "espnet/kan-bayashi_ljspeech_vits"
            ]
        }
        
    def generate_text(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate text using Hugging Face models"""
        if not self.api_key:
            return self._simulate_text_generation(prompt)
            
        try:
            # Use specified model or default
            model_id = model or self.models["text_generation"][0]
            
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    return result[0].get("generated_text", "No text generated")
                return result.get("generated_text", "No text generated")
            else:
                return f"Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"HF text generation error: {e}")
            return self._simulate_text_generation(prompt)
    
    def generate_image(self, prompt: str, model: Optional[str] = None) -> str:
        """Generate image using Hugging Face models"""
        if not self.api_key:
            return self._simulate_image_generation(prompt)
            
        try:
            # Use Stable Diffusion by default
            model_id = model or self.models["image_generation"][0]
            
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {"inputs": prompt}
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                # Save image
                import base64
                from pathlib import Path
                from datetime import datetime
                
                image_data = response.content
                filename = f"generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = Path("generated_images") / filename
                filepath.parent.mkdir(exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    f.write(image_data)
                    
                return f"🎨 Image generated successfully!\n📁 Saved as: {filepath}\n📝 Prompt: {prompt}"
            else:
                return f"Error generating image: {response.status_code}"
                
        except Exception as e:
            logger.error(f"HF image generation error: {e}")
            return self._simulate_image_generation(prompt)
    
    def translate(self, text: str, target_lang: str = "en") -> str:
        """Translate text using Hugging Face models"""
        if not self.api_key:
            return f"[Translation to {target_lang}] {text}"
            
        try:
            model_id = self.models["translation"][0]
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": text,
                "parameters": {"src_lang": "en", "tgt_lang": target_lang}
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    return result[0].get("translation_text", "Translation failed")
                return result.get("translation_text", "Translation failed")
            else:
                return f"Translation error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"HF translation error: {e}")
            return f"[Translation to {target_lang}] {text}"
    
    def summarize(self, text: str, max_length: int = 150) -> str:
        """Summarize text using Hugging Face models"""
        if not self.api_key:
            return f"Summary: {text[:200]}..."
            
        try:
            model_id = self.models["summarization"][0]
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": text,
                "parameters": {
                    "max_length": max_length,
                    "min_length": 30,
                    "do_sample": False
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    return result[0].get("summary_text", "Summary failed")
                return result.get("summary_text", "Summary failed")
            else:
                return f"Summarization error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"HF summarization error: {e}")
            return f"Summary: {text[:200]}..."
    
    def answer_question(self, context: str, question: str) -> str:
        """Answer questions based on context"""
        if not self.api_key:
            return f"Based on context: {context[:100]}...\nQuestion: {question}\nAnswer would appear here."
            
        try:
            model_id = self.models["question_answering"][0]
            API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            payload = {
                "inputs": {
                    "question": question,
                    "context": context
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("answer", "No answer found")
            else:
                return f"QA error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"HF QA error: {e}")
            return "Unable to answer question at this time."
    
    def _simulate_text_generation(self, prompt: str) -> str:
        """Simulate text generation when API unavailable"""
        return f"""**Generated Text (Simulated)**

Based on your prompt: "{prompt[:100]}..."

I can help generate text, but for full functionality, please:

1. Get a Hugging Face API key from https://huggingface.co/settings/tokens
2. Set it as environment variable: export HUGGINGFACE_API_KEY="your-key"
3. Or add to ~/.skatlaz_config.json

The following Hugging Face models are available with your API key:

✨ **Text Generation Models:**
   - mistralai/Mistral-7B-Instruct-v0.1
   - google/flan-t5-large
   - meta-llama/Llama-2-7b-chat-hf

🎨 **Image Generation Models:**
   - stabilityai/stable-diffusion-2-1
   - runwayml/stable-diffusion-v1-5

📝 **Summarization Models:**
   - facebook/bart-large-cnn
   - t5-large

🌐 **Translation Models:**
   - facebook/m2m100_418M
   - Helsinki-NLP/opus-mt-en-es

To use these, simply mention what you want to generate, and I'll use the appropriate model!"""
    
    def _simulate_image_generation(self, prompt: str) -> str:
        """Simulate image generation when API unavailable"""
        return f"""**Image Generation (Simulated)**

Prompt: "{prompt}"

To generate actual images, please:

1. Get Hugging Face API key
2. Install Pillow: pip install Pillow
3. Use models like:
   - stabilityai/stable-diffusion-2-1
   - runwayml/stable-diffusion-v1-5

Example with API key:
```python
from modules.huggingface_apps import HuggingFaceApps
hf = HuggingFaceApps()
result = hf.generate_image("beautiful sunset over mountains")"""
