#pip install transformers accelerate bitsandbytes
import torch
import requests
import spacy
from transformers import pipeline
from diffusers import AutoPipelineForText2Image
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from googleapiclient.discovery import build
import threading

MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
# ou:
# MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    load_in_4bit=True
)

# =========================
# CONFIG
# =========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

BING_API_KEY = "SUA_CHAVE_AQUI"
BING_ENDPOINT = "https://api.bing.microsoft.com/v7.0/search"

# =========================
# MODELOS
# =========================
nlp = spacy.load("en_core_web_sm")

text_generator = pipeline(
    "text-generation",
    model_name = "gpt2",
    tokenizer = AutoTokenizer.from_pretrained(model_name),
    model = AutoModelForCausalLM.from_pretrained(model_name).to(DEVICE),
    device=0 if DEVICE == "cuda" else -1
)

image_generator = AutoPipelineForText2Image.from_pretrained(
    "ZhengPeng7/Z-Image-Turbo",
    torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32
).to(DEVICE)

def generate_text_stream(prompt):
    entities = extract_entities(prompt)
    search_query = " ".join(entities) if entities else prompt

    try:
        context_web = search_bing(search_query)
    except:
        context_web = ""

    context_memory = memory.get_context()

    final_prompt = format_prompt(prompt, context_memory, context_web)

    inputs = tokenizer(final_prompt, return_tensors="pt").to(model.device)

    streamer = TextIteratorStreamer(
        tokenizer,
        skip_prompt=True,
        skip_special_tokens=True
    )

    generation_kwargs = dict(
        **inputs,
        streamer=streamer,
        max_new_tokens=300,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

    thread = threading.Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()

    print("\nAssistente: ", end="", flush=True)

    full_response = ""

    for token in streamer:
        print(token, end="", flush=True)
        full_response += token

    print("\n")
    return full_response

def chat(user_input):
    if is_image_request(user_input):
        response = generate_image(user_input)
        print("\nAssistente:", response)
    else:
        response = generate_text_stream(user_input)

    memory.add(user_input, response)
    return response
    
# =========================
# MEMÓRIA (estilo chat)
# =========================
class Memory:
    def __init__(self, max_turns=5):
        self.history = []
        self.max_turns = max_turns

    def add(self, user, assistant):
        self.history.append({"user": user, "assistant": assistant})

        # mantém só últimas interações
        if len(self.history) > self.max_turns:
            self.history.pop(0)

    def get_context(self):
        context = ""
        for turn in self.history:
            context += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n"
        return context


memory = Memory()

# =========================
# NLP
# =========================
def extract_entities(prompt):
    doc = nlp(prompt)
    allowed = {"ORG", "PERSON", "GPE", "PRODUCT", "EVENT"}
    return [ent.text for ent in doc.ents if ent.label_ in allowed]

# =========================
# BING SEARCH
# =========================
def search_bing(query):
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": 3}

    response = requests.get(BING_ENDPOINT, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()

    results = []
    if "webPages" in data:
        for item in data["webPages"]["value"]:
            results.append(item["snippet"])

    return " ".join(results)

# =========================
# TEXTO (COM MEMÓRIA + RAG)
# =========================
def generate_text(prompt):

    entities = extract_entities(prompt)
    search_query = " ".join(entities) if entities else prompt

    try:
        context_web = search_console_api(search_query)
    except:
        context_web = ""

    context_memory = memory.get_context()

    final_prompt = f"""
    Histórico:
    {context_memory}

    Contexto externo:
    {context_web}

    Usuário:
    {prompt}

    Assistente:
    """

def search_console_api(query, api_key, cx, num_resultados=5):
    try:
        service = build("customsearch", "v1", developerKey=api_key)

        resultado = service.cse().list(
            q=query,
            cx=cx,
            num=num_resultados
        ).execute()

        itens = resultado.get("items", [])

        resultados_formatados = []
        for item in itens:
            resultados_formatados.append({
                "titulo": item.get("title"),
                "link": item.get("link"),
                "descricao": item.get("snippet")
        })

        return resultados_formatados

    except Exception as e:
        print("Erro na pesquisa:", e)
        return []


    # 🔑 Substitua pelos seus dados
    API_KEY = "SUA_API_KEY"
    CX = "SEU_SEARCH_ENGINE_ID"

    # 🔍 Exemplo de uso
    resultados = pesquisar_google("inteligência artificial", API_KEY, CX)

    for i, r in enumerate(resultados, 1):
        print(f"\nResultado {i}")
        print("Título:", r["titulo"])
        print("Link:", r["link"])
        print("Descrição:", r["descricao"])
    response = text_generator(
        final_prompt,
        max_length=300,
        do_sample=True,
        temperature=0.7
    )[0]["generated_text"]

    return response

# =========================
# IMAGEM
# =========================
def generate_image(prompt):
    image = image_generator(
        prompt,
        num_inference_steps=4,
        guidance_scale=0.0
    ).images[0]

    file_name = "output.png"
    image.save(file_name)

    return f"Imagem salva como {file_name}"
    
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_name = "deepseek-ai/deepseek-coder-6.7b-instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto"
)


# =========================
# CODE
# =========================


def generate_code(user_input):
    prompt = f"""
You are a senior software engineer.

Your task is to generate clean, efficient, and well-documented code.

User request:
{user_input}
"""

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")

    outputs = model.generate(
        **inputs,
        max_new_tokens=500,
        temperature=0.2,
        top_p=0.9
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# =========================
# ROUTER
# =========================
def is_image_request(prompt):
    keywords = ["imagem", "foto", "desenho", "ilustração", "gere uma imagem"]
    return any(k in prompt.lower() for k in keywords)

def chat(user_input):
    if is_image_request(user_input):
        response = generate_image(user_input)
    if is_code_request(user_input):
    # Teste
        response = generate_code(user_input)
    else:
        response = generate_text(user_input)
    memory.add(user_input, response)
    return response

# =========================
# LOOP PRINCIPAL
# =========================
if __name__ == "__main__":
    print("🤖 ChatGPT-like iniciado (com memória + busca + imagem)\n")

    while True:
        user_input = input("Você: ")

        if user_input.lower() in ["sair", "exit", "quit"]:
            break

        resposta = chat(user_input)
        print("\nAssistente:", resposta, "\n")
