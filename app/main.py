from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import torch.nn.functional as F
from peft import LoraConfig, PeftModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cambia esto por el nombre de tu modelo en Hugging Face
MODEL_NAME = "app/modelo_qwen_sql_final"

# Cargar modelo y tokenizer UNA sola vez al iniciar la app
tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-Coder-1.5B')
tokenizer.pad_token = tokenizer.eos_token

base_model = AutoModelForCausalLM.from_pretrained(
        'Qwen/Qwen2.5-Coder-1.5B', torch_dtype=torch.float16, device_map="auto"
    )

model = PeftModel.from_pretrained(base_model, MODEL_NAME)

class GenerateRequest(BaseModel):
    pregunta: str
    contexto: str

@app.post("/predict")
def predict(request: GenerateRequest):

    prompt = f"Pregunta: {request.pregunta}\nContexto: {request.contexto}\nSQL: "
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=64, temperature=0.01, do_sample=False,
            eos_token_id=tokenizer.eos_token_id
        )
    decode = tokenizer.decode(outputs[0], skip_special_tokens=True)

    lineas = decode.strip().split("\n")

    pregunta = lineas[0].split(":", 1)[1].strip()
    contexto = lineas[1].split(":", 1)[1].strip()
    sql = lineas[2].split(":", 1)[1].strip()

    
    return {
        "pregunta": pregunta,
        "contexto" : contexto,
        "sql" : sql
    }
