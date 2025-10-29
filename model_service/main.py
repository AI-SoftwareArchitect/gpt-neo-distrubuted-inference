from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import hashlib

import threading

MODEL_DIR = "./gpt_neo_125m_finetuned/checkpoint-279"
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForCausalLM.from_pretrained(MODEL_DIR).to("cuda")
model.eval()

app = FastAPI()

# Memory cache: prompt hash -> generated text
cache = {}
cache_lock = threading.Lock()  # thread-safe cache

class Prompt(BaseModel):
    text: str

def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

@app.post("/generate")
def generate(prompt: Prompt):
    key = prompt_hash(prompt.text)
    
    # Cache kontrolü
    with cache_lock:
        if key in cache:
            return {"generated_text": cache[key], "cached": True}
    
    inputs = tokenizer(prompt.text, return_tensors="pt").to("cuda")
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            top_p=0.9,
            temperature=0.8
        )
    result = tokenizer.decode(output[0], skip_special_tokens=True)
    
    with cache_lock:
        cache[key] = result  # cache memory'de
    
    return {"generated_text": result, "cached": False}
