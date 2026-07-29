import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

# Pasta para armazenar STL
os.makedirs("stl_files", exist_ok=True)

# Disponibiliza arquivos STL
app.mount("/stl", StaticFiles(directory="stl_files"), name="stl")


class MvpRequest(BaseModel):
    user_prompt: str


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/generate-mvp")
async def generate_mvp(request: MvpRequest):

    prompt = request.user_prompt.strip()

    if len(prompt) < 3:
        return JSONResponse(
            {
                "success": False,
                "error": "Descreva melhor o objeto."
            }
        )

    # Exemplo:
    # aqui você substituirá pela geração real do STL.
    # O sistema só devolve o arquivo já pronto.

    arquivo_stl = "modelo_demo.stl"

    justificativa = f"""
Modelo criado para:

{prompt}

O arquivo STL foi preparado para visualização e download.
"""

    return {
        "success": True,
        "justificativa": justificativa,
        "arquivo_stl_url": f"/stl/{arquivo_stl}"
    }
