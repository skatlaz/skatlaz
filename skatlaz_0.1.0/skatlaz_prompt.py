# =========================
# INSTALL
# pip install transformers accelerate bitsandbytes diffusers spacy requests google-api-python-client
# python -m spacy download en_core_web_sm
# pip install gradio_client pillow
# =========================

import torch
import requests
import spacy
import threading
import torch
from gradio_client import Client
from PIL import Image
import time
from bs4 import BeautifulSoup
from googlesearch import search
from datasets import load_dataset
from smolagents import ToolCallingAgent, tool
import datetime
import random

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer
)

from diffusers import AutoPipelineForText2Image

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Configure 4-bit quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load model with quantization_config
model_id = "mistralai/Mistral-7B-Instruct-v0.3"
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_id)


from googleapiclient.discovery import build


# =========================
# CONFIG
# =========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_TEXT = "mistralai/Mistral-7B-Instruct-v0.2"
MODEL_CODE = "deepseek-ai/deepseek-coder-6.7b-instruct"
MODEL_IMAGE = "ZhengPeng7/Z-Image-Turbo"

BING_API_KEY = ""
GOOGLE_API_KEY = ""
GOOGLE_CX = ""

# =========================
# LOAD MODELS (LAZY)
# =========================
_tokenizer = None
_model = None

_code_tokenizer = None
_code_model = None

_image_model = None

nlp = spacy.load("en_core_web_sm")


def load_text_model():
    global _tokenizer, _model
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_TEXT)
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_TEXT,
            device_map="auto",
            load_in_4bit=True
        )
    return _tokenizer, _model


def load_code_model():
    global _code_tokenizer, _code_model
    if _code_model is None:
        _code_tokenizer = AutoTokenizer.from_pretrained(MODEL_CODE)
        _code_model = AutoModelForCausalLM.from_pretrained(
            MODEL_CODE,
            device_map="auto",
            torch_dtype=torch.float16
        )
    return _code_tokenizer, _code_model


def load_image_model():
    global _image_model
    if _image_model is None:
        _image_model = AutoPipelineForText2Image.from_pretrained(
            MODEL_IMAGE,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
        ).to(DEVICE)
    return _image_model


# =========================
# MEMORY
# =========================
class Memory:
    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns

    def add(self, user, assistant):
        self.history.append({"user": user, "assistant": assistant})
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def context(self):
        return "\n".join(
            f"User: {t['user']}\nAssistant: {t['assistant']}"
            for t in self.history
        )


memory = Memory()


# =========================
# NLP
# =========================
def extract_entities(text):
    doc = nlp(text)
    allowed = {"ORG", "PERSON", "GPE", "PRODUCT", "EVENT"}
    return [e.text for e in doc.ents if e.label_ in allowed]


# =========================
# SEARCH (RAG)
# =========================
def search_bing(query):
    if not BING_API_KEY:
        return ""

    try:
        headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
        params = {"q": query, "count": 3}

        res = requests.get(
            "https://api.bing.microsoft.com/v7.0/search",
            headers=headers,
            params=params
        )
        res.raise_for_status()

        data = res.json()

        return " ".join(
            item["snippet"]
            for item in data.get("webPages", {}).get("value", [])
        )

    except:
        return ""


# =========================
# PROMPT BUILDER
# =========================
def build_prompt(user_input):
    entities = extract_entities(user_input)
    query = " ".join(entities) if entities else user_input

    web_context = search_bing(query)
    mem_context = memory.context()

    return f"""
You are a helpful AI assistant.

Conversation:
{mem_context}

External context:
{web_context}

User:
{user_input}

Assistant:
"""

# =========================
# 🧠 MEMORY SIMPLE
# =========================
class Memory:
    def __init__(self):
        self.data = []

    def add(self, user, assistant):
        self.data.append({
            "user": user,
            "assistant": assistant,
            "timestamp": time.time()
        })

memory = Memory()

# =========================
# 🧠 INTENT DETECTION (melhorado)
# =========================
def is_image(text: str) -> bool:
    keywords = ["imagem", "desenhe", "gerar imagem", "ilustração", "foto de"]
    return any(k in text.lower() for k in keywords)


def is_code(text: str) -> bool:
    keywords = ["código", "python", "script", "programa", "função", "api"]
    return any(k in text.lower() for k in keywords)


def is_weather(text: str) -> bool:
    keywords = ["clima", "tempo", "temperatura", "chuva", "previsão do tempo"]
    return any(k in text.lower() for k in keywords)

# =========================
# 🔎 WEB SEARCH TOOL
# =========================
@tool
def google_search(query: str) -> str:
    """Pesquisa no Google e retorna links resumidos"""
    try:
        results = []
        for url in search(query, num_results=5):
            results.append(url)
        return "\n".join(results)
    except Exception as e:
        return f"Erro na busca: {str(e)}"


# =========================
# 🌐 WEB SCRAPER TOOL
# =========================
@tool
def web_scraper(url: str) -> str:
    """Extrai texto de uma página web"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        texts = soup.get_text(separator=" ", strip=True)
        return texts[:3000]  # limita tamanho
    except Exception as e:
        return f"Erro ao acessar site: {str(e)}"


# =========================
# 🌦️ FAKE WEATHER TOOL (API fallback)
# =========================
@tool
def weather(city: str) -> str:
    """Simula previsão do tempo (substituível por API real)"""
    temps = random.randint(15, 35)
    conditions = ["ensolarado", "nublado", "chuva leve", "tempestade", "ventando"]
    return f"Clima em {city}: {temps}°C e {random.choice(conditions)}"

# =========================
# 🌦️ WEATHER API REAL (OPEN-METEO)
# =========================
def get_weather(city: str):
    try:
        # 1. geocoding
        geo = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        ).json()

        if "results" not in geo:
            return "Cidade não encontrada."

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]
        name = geo["results"][0]["name"]

        # 2. weather
        weather = requests.get(
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        ).json()

        temp = weather["current_weather"]["temperature"]
        wind = weather["current_weather"]["windspeed"]

        return f"🌦️ Clima em {name}: {temp}°C | vento {wind} km/h"

    except Exception as e:
        return f"Erro no clima: {str(e)}"


# =========================
# 📚 FINEWEB SAMPLE TOOL
# =========================
@tool
def fineweb_sample(query: str) -> str:
    """Busca exemplos no dataset FineWeb (Hugging Face)"""
    try:
        ds = load_dataset("HuggingFaceFW/fineweb", split="train", streaming=True)

        results = []
        for i, item in enumerate(ds):
            text = item.get("text", "")
            if query.lower() in text.lower():
                results.append(text[:300])
            if len(results) >= 3:
                break

        return "\n---\n".join(results) if results else "Nenhum resultado encontrado."
    except Exception as e:
        return f"Erro FineWeb: {str(e)}"


# =========================
# 📖 STORY GENERATOR TOOL
# =========================
@tool
def story_generator(prompt: str) -> str:
    """Gera histórias simples baseadas em prompt"""
    templates = [
        f"Era uma vez em {prompt}, um evento inesperado mudou tudo...",
        f"No mundo de {prompt}, um herói improvável surgiu das sombras...",
        f"Em {prompt}, segredos antigos começaram a ser revelados..."
    ]
    return random.choice(templates)


# =========================
# 🧠 SIMPLE LLM CORE (HF optional)
# =========================
class SimpleLLM:
    def __init__(self):
        self.history = []

    def chat(self, message: str) -> str:
        """Fallback LLM simples (sem API externa)"""
        self.history.append(message)

        # lógica simples estilo QA
        if "tempo" in message.lower():
            return "Use a tool weather(city) para previsão do tempo."
        if "pesquisa" in message.lower():
            return "Use google_search(query) para buscar informações."
        if "história" in message.lower():
            return "Use story_generator(prompt) para criar histórias."
        if "web" in message.lower():
            return "Use web_scraper(url) para extrair conteúdo."

        return f"Resposta simulada: entendi sua pergunta -> {message}"


# =========================
# 🤖 AGENTE PRINCIPAL
# =========================
llm = SimpleLLM()

agent = ToolCallingAgent(
    tools=[
        google_search,
        web_scraper,
        weather,
        fineweb_sample,
        story_generator
    ],
    llm=llm
)


# =========================
# TEXT GENERATION (STREAM)
# =========================
def generate_text_stream(prompt):
    tokenizer, model = load_text_model()

    final_prompt = build_prompt(prompt)

    inputs = tokenizer(final_prompt, return_tensors="pt").to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    thread = threading.Thread(
        target=model.generate,
        kwargs=dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=300,
            temperature=0.7,
            top_p=0.9
        )
    )
    thread.start()

    response = ""

    for token in streamer:
        print(token, end="", flush=True)
        response += token

    print()
    return response


# =========================
# IMAGE
# =========================

# URL do Space
SPACE_ID = "mrfakename/Z-Image-Turbo"

client = Client(SPACE_ID)

def generate_image(prompt, height=1024, width=1024, steps=8, seed=None):
    print("🔄 Gerando imagem...")

    if seed is None:
        seed = int(time.time()) % 2**32

    result = client.predict(
        prompt,
        height,
        width,
        steps,
        seed,
        True,  # randomize_seed
        api_name="/generate_image"
    )

    # O retorno geralmente é (imagem, seed)
    image_path, used_seed = result

    print(f"✅ Seed usada: {used_seed}")


# =========================
# CODE
# =========================
def generate_code(prompt):
    tokenizer, model = load_code_model()

    full_prompt = f"""
You are a senior software engineer.

Task:
{prompt}
"""

    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=500,
        temperature=0.2
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)

# =========================
# 🧠 TEXT GENERATION
# =========================
def generate_text_stream(text):
    return f"🧠 Resposta gerada: {text}"
    
# =========================
# ROUTER
# =========================
def is_image(prompt):
    return any(k in prompt.lower() for k in ["image", "foto", "desenho"])


def is_code(prompt):
    return any(k in prompt.lower() for k in ["code", "api", "programa"])


def chat(user_input):

    # 🌦️ WEATHER FIRST (melhor UX)
    if is_weather(user_input):
        city = user_input.replace("clima", "").replace("tempo", "").strip()
        response = get_weather(city)

    # 🖼️ IMAGE
    elif is_image(user_input):
        img = generate_image(
            user_input,
            height=1024,
            width=1024,
            steps=8
        )

        output_file = "imagem_gerada.png"
        img.save(output_file)

        print(f"📁 Imagem salva como {output_file}")
        img.show()

        response = f"Imagem gerada: {output_file}"

    # 💻 CODE
    elif is_code(user_input):
        response = generate_code(user_input)

    # 🧠 TEXT / LLM
    else:
        response = generate_text_stream(user_input)

    # 💾 MEMORY
    memory.add(user_input, response)

    return response


# =========================
# CLI LOOP
# =========================
if __name__ == "__main__":
    print("🤖 Skatlaz AI iniciado\n")

    while True:
        user = input("Você: ")

        if user.lower() in ["exit", "quit"]:
            break

        print("\nAssistente:", end=" ")
        chat(user)
