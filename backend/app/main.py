from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import torch.nn.functional as F
from peft import LoraConfig, PeftModel
from fastapi.middleware.cors import CORSMiddleware

# Cambia esto por el nombre de tu modelo en Hugging Face
MODEL_NAME = "app/modelo_qwen_sql_final"

# Check if CUDA (GPU) or MPS (Apple Silicon GPU) is available
if torch.cuda.is_available():
    device = "cuda"
    dtype = torch.float16
elif torch.backends.mps.is_available():
    device = "mps"
    dtype = torch.float16
else:
    # Essential for Intel i5 x86_64 without GPU, and Docker on Mac M4.
    # We use bfloat16 to halve the memory footprint (from ~6GB to ~3GB)
    # to prevent Docker Desktop from killing the container due to OOM (Exit 137).
    device = "cpu"
    dtype = torch.bfloat16

# Global variables for models
tokenizer = None
base_model = None
model = None
model_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global tokenizer, base_model, model, model_ready
    print("Iniciando descarga/carga del modelo en background...")

    try:
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-Coder-1.5B")
        tokenizer.pad_token = tokenizer.eos_token

        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen2.5-Coder-1.5B", torch_dtype=dtype, device_map=device
        )
        model = PeftModel.from_pretrained(base_model, MODEL_NAME)
        model_ready = True
        print("¡Modelo cargado exitosamente y listo para inferir!")
    except Exception as e:
        print(f"Error crítico cargando el modelo: {e}")

    yield
    # Cleanup on shutdown (optional)


app = FastAPI(lifespan=lifespan)


class GenerateRequest(BaseModel):
    pregunta: str
    contexto: str


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """
    Returns 200 OK if the model has finished downloading/loading.
    Returns 503 if the model is still being processed.
    """
    if model_ready:
        return {"status": "ready"}
    else:
        raise HTTPException(
            status_code=503,
            detail="Model is currently downloading/loading. Please wait.",
        )


@app.post("/predict")
def predict(request: GenerateRequest):
    if not model_ready:
        raise HTTPException(status_code=503, detail="Model not ready yet.")

    prompt = f"Pregunta: {request.pregunta}\nContexto: {request.contexto}\nSQL: "
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=64,
            temperature=0.01,
            do_sample=False,
            eos_token_id=tokenizer.eos_token_id,
        )
    decode = tokenizer.decode(outputs[0], skip_special_tokens=True)

    lineas = decode.strip().split("\n")

    pregunta = lineas[0].split(":", 1)[1].strip()
    contexto = lineas[1].split(":", 1)[1].strip()
    sql = lineas[2].split(":", 1)[1].strip()

    return {"pregunta": pregunta, "contexto": contexto, "sql": sql}
