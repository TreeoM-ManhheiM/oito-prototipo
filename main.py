import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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

# Inicia o cliente da API do Groq utilizando a chave configurada no Render
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Filtros de Segurança e Moderação Escolar da SEDUC
TERMOS_PROIBIDOS = [
    "penis", "pênis", "vagina", "vulva", "caralho", "bunda", "dildo", "erotico", "erótico",
    "armas", "faca", "bomba", "cassino", "briga", "droga", "maconha", "cocaína",
    "cerveja", "vodka", "cachaça", "bebida", "narguile", "vape", "cigarro"
]

class MvpRequest(BaseModel):
    user_prompt: str

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

# ROTA EXCLUSIVA: Gerador de Códigos de MVP 3D Open Source
@app.post("/generate-mvp")
async def generate_mvp_endpoint(request: MvpRequest):
    prompt_limpo = request.user_prompt.lower()
    
    # Validação prévia de segurança na lista negra
    if any(termo in prompt_limpo for termo in TERMOS_PROIBIDOS):
        return {
            "success": False,
            "error": "🚨 ALERTA DE SEGURANÇA: O pedido contém termos inadequados que violam as diretrizes da escola."
        }
    
    system_prompt = """
    Você é um Engenheiro de Prototipagem especialista em OpenSCAD para a ementa de Inovação e Empreendedorismo.
    Sua função é receber a ideia de um aluno e gerar exclusivamente a análise de negócios do MVP e o script OpenSCAD funcional.

    REGRA DE CONTEXTO COMERCIAL:
    Se o objeto pedido não tiver aplicação comercial/industrial ou pedagógica (como armas ou personagens puramente decorativos), recuse a geração solicitando que justifiquem a startup.

    Sua resposta DEVE seguir estritamente essa estrutura dividida pela marcação [DIVISOR_CODIGO]:
    
    Empreendedorismo e Justificativa Comercial do MVP:
    (Explique aqui em poucas linhas como este objeto serve como MVP, validação de mercado ou brinde da marca).

    [DIVISOR_CODIGO]
    // Apenas o código OpenSCAD limpo a partir daqui
    (Insira o código completo OpenSCAD usando geometrias como cube, cylinder, sphere, union, difference, text. Proporções até 100mm).
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_prompt}
            ],
            model="llama-3.2-11b-vision-preview",
            temperature=0.2
        )
        full_response = chat_completion.choices[0].message.content

        justificativa = "Não foi possível gerar a análise."
        codigo_scad = ""

        if "[DIVISOR_CODIGO]" in full_response:
            parts = full_response.split("[DIVISOR_CODIGO]")
            justificativa = parts[0].strip()
            codigo_scad = parts[1].strip()
            # Remove possíveis blocos de markdown que a IA coloque por vício
            codigo_scad = codigo_scad.replace("```scad", "").replace("```openscad", "").replace("```", "").strip()
        else:
            justificativa = full_response

        return {
            "success": True,
            "justificativa": justificativa,
            "codigo_scad": codigo_scad
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao processar modelo 3D: {str(e)}"}
