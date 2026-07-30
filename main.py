import os
import subprocess
import tempfile
import base64
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

# Inicia o cliente da API do Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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

@app.post("/generate-mvp")
async def generate_mvp_endpoint(request: MvpRequest):
    prompt_limpo = request.user_prompt.lower()
    
    if any(termo in prompt_limpo for termo in TERMOS_PROIBIDOS):
        return {
            "success": False,
            "error": "🚨 ALERTA DE SEGURANÇA: O pedido contém termos inadequados que violam as diretrizes da escola."
        }
    
    system_prompt = """
    Você é um Engenheiro de Prototipagem especialista em OpenSCAD para a ementa de Inovação e Empreendedorismo.
    Sua função é receber a ideia de um aluno e gerar exclusivamente a análise de negócios do MVP e o script OpenSCAD funcional.

    REGRA DE CONTEXTO COMERCIAL:
    Se o objeto pedido não tiver aplicação comercial/industrial ou pedagógica, recuse a geração solicitando que justifiquem a startup.

    Sua resposta DEVE seguir estritamente essa estrutura dividida pela marcação [DIVISOR_CODIGO]:
    
    Empreendedorismo e Justificativa Comercial do MVP:
    (Explique aqui em poucas linhas como este objeto serve como MVP, validação de mercado ou brinde da marca).

    [DIVISOR_CODIGO]
    // Apenas o código OpenSCAD limpo a partir daqui
    (Insira o código completo OpenSCAD usando geometrias como cube, cylinder, sphere, union, difference, text. Proporções até 100mm. Não use acentos no text).
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2
        )
        full_response = chat_completion.choices[0].message.content

        if "[DIVISOR_CODIGO]" not in full_response:
            return {"success": True, "justificativa": full_response, "codigo_scad": "", "stl_base64": None}

        parts = full_response.split("[DIVISOR_CODIGO]")
        justificativa = parts[0].strip()
        codigo_scad = parts[1].strip().replace("```scad", "").replace("```openscad", "").replace("```", "").strip()

        # CONVERSÃO SCAD PARA STL NO SERVIDOR
        stl_base64 = None
        try:
            # Cria arquivos temporários
            with tempfile.NamedTemporaryFile(suffix=".scad", delete=False) as f_scad:
                f_scad.write(codigo_scad.encode('utf-8'))
                scad_path = f_scad.name
            
            stl_path = scad_path.replace(".scad", ".stl")
            
            # Executa o OpenSCAD via linha de comando
            subprocess.run(["openscad", "-o", stl_path, scad_path], check=True, capture_output=True)
            
            # Lê o STL gerado e converte para Base64 para enviar via JSON ao index.html
            with open(stl_path, "rb") as f_stl:
                stl_base64 = base64.b64encode(f_stl.read()).decode('utf-8')
                
            # Limpeza
            os.remove(scad_path)
            os.remove(stl_path)
        except Exception as conv_e:
            print(f"Erro na conversão STL: {conv_e}")
            pass 

        return {
            "success": True,
            "justificativa": justificativa,
            "codigo_scad": codigo_scad,
            "stl_base64": stl_base64
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao processar modelo 3D: {str(e)}"}
