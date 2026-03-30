#skatlaz_llms_prompt.py

# =========================
# INSTALL
# pip install transformers accelerate bitsandbytes diffusers spacy requests
# python -m spacy download en_core_web_sm
# =========================

import torch
import requests
import spacy
import threading

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TextIteratorStreamer
)

from diffusers import AutoPipelineForText2Image

# =========================
# CONFIG
# =========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

MODEL_TEXT = "mistralai/Mistral-7B-Instruct-v0.2"
MODEL_CODE = "deepseek-ai/deepseek-coder-6.7b-instruct"
MODEL_IMAGE = "stabilityai/sdxl-turbo"

BING_API_KEY = ""  # opcional

# =========================
# NLP
# =========================
nlp = spacy.load("en_core_web_sm")

# =========================
# LAZY LOAD MODELS
# =========================
_text_tokenizer = None
_text_model = None

_code_tokenizer = None
_code_model = None

_image_model = None


def load_text_model():
    global _text_tokenizer, _text_model

    if _text_model is None:
        _text_tokenizer = AutoTokenizer.from_pretrained(MODEL_TEXT)

        _text_model = AutoModelForCausalLM.from_pretrained(
            MODEL_TEXT,
            device_map="auto",
            load_in_4bit=True
        )

    return _text_tokenizer, _text_model


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
# NLP UTIL
# =========================
def extract_entities(text):
    doc = nlp(text)
    allowed = {"ORG", "PERSON", "GPE", "PRODUCT", "EVENT"}
    return [ent.text for ent in doc.ents if ent.label_ in allowed]


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

    except Exception:
        return ""


# =========================
# PROMPT BUILDER
# =========================
def build_prompt(user_input, memory_context=""):
    entities = extract_entities(user_input)
    query = " ".join(entities) if entities else user_input

    web_context = search_bing(query)

    return f"""
You are SKATLAZ AI.

- intelligent
- precise
- capable of coding, research, and reasoning

Conversation:
{memory_context}

External context:
{web_context}

User:
{user_input}

Assistant:
"""


# =========================
# TEXT GENERATION (STREAM)
# =========================
def generate_text_stream(prompt, memory_context=""):
    tokenizer, model = load_text_model()

    final_prompt = build_prompt(prompt, memory_context)

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
            max_new_tokens=400,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
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
# TEXT (NON-STREAM)
# =========================
def generate_text(prompt, memory_context=""):
    tokenizer, model = load_text_model()

    final_prompt = build_prompt(prompt, memory_context)

    inputs = tokenizer(final_prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=400,
        temperature=0.7,
        top_p=0.9
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)


# =========================
# ARTICLE GENERATION
# =========================

def generate_article(prompt):
    return generate_text(f"""
Write a detailed article about:

{prompt}

Include:
- Title
- Sections
- Examples
- Conclusion
""")

# =========================
# CODE GENERATION
# =========================
def generate_code(prompt):
    tokenizer, model = load_code_model()

    full_prompt = f"""
You are a senior software engineer.

Write clean, efficient, production-ready code.

Task:
{prompt}
"""

    inputs = tokenizer(full_prompt, return_tensors="pt").to(model.device)

    output = model.generate(
        **inputs,
        max_new_tokens=600,
        temperature=0.2,
        top_p=0.9
    )

    return tokenizer.decode(output[0], skip_special_tokens=True)


# =========================
# IMAGE GENERATION
# =========================
def generate_image(prompt):
    model = load_image_model()

    image = model(
        prompt,
        num_inference_steps=4,
        guidance_scale=0.0
    ).images[0]

    file_name = "output.png"
    image.save(file_name)

    return f"Image saved as {file_name}"


# =========================
# GAME GENERATION
# =========================
def generate_game(prompt):
    return generate_code(f"""
Create a simple game.

Requirements:
{prompt}

Use Python (pygame) or HTML5.
Include instructions.
""")


# =========================
# SMART ROUTER
# =========================
def smart_router(prompt):
    p = prompt.lower()

    if any(k in p for k in ["imagem", "image", "foto", "desenho"]):
        return generate_image(prompt)

    if any(k in p for k in ["game", "jogo"]):
        return generate_game(prompt)

    if any(k in p for k in ["code", "código", "api", "programa"]):
        return generate_code(prompt)

    if any(k in p for k in ["research", "pesquisa"]):
        return generate_text(f"Write a detailed research about: {prompt}")

    return generate_text(prompt)
