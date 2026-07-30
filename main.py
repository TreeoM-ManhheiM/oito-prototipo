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
    Você é um Engenheiro de Prototipagem e Professor especialista em OpenSCAD, atuando no laboratório de Inovação e Empreendedorismo da SEDUC.
    Sua função é receber a ideia de um aluno e gerar exclusivamente a análise de negócios do MVP e o script OpenSCAD funcional.

    🚨 REGRAS DE SEGURANÇA E ESCOPO EDUCACIONAL:
    - RECUSE IMEDIATAMENTE qualquer pedido envolvendo armas, violência, drogas, conteúdo erótico ou brincadeiras sem foco pedagógico/comercial.
    - Se recusar, utilize a justificativa para dar uma orientação educacional firme e peça uma nova ideia válida. Deixe a área do código em branco.

    🚨 REGRAS TÉCNICAS OBRIGATÓRIAS DE DESIGN:
    1. A PRIMEIRA linha do código DEVE ser obrigatoriamente: $fn = 100;
    2. Crie geometrias sólidas e limpas usando apenas primitivas (cube, cylinder, sphere).
    3. Para fazer chaveiros com furo na ponta, você DEVE envelopar tudo dentro de um difference() e usar translate() no cilindro.
    4. É ESTRITAMENTE PROIBIDO usar crases de formatação Markdown (como ```scad) no código.
    5. Todas as instruções OpenSCAD DEVEM terminar com ponto e vírgula (;).

    Sua resposta DEVE seguir estritamente essa estrutura dividida pela marcação [DIVISOR_CODIGO]:
    
    Empreendedorismo e Justificativa Comercial do MVP:
    (Explique em poucas linhas como este objeto serve como MVP ou justifique a recusa).

    [DIVISOR_CODIGO]
    // O código OpenSCAD limpo começa aqui.
    // EXEMPLO OBRIGATÓRIO DE CHAVEIRO COM FURO NA PONTA:
    // $fn = 100;
    // difference() {
    //    cube([60, 30, 3], center=true);
    //    translate([23, 0, 0]) cylinder(h=10, r=2, center=true);
    // }
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1
        )
        full_response = chat_completion.choices[0].message.content

        if "[DIVISOR_CODIGO]" not in full_response:
            return {"success": True, "justificativa": full_response, "codigo_scad": "", "stl_base64": None}

        parts = full_response.split("[DIVISOR_CODIGO]")
        justificativa = parts[0].strip()
        codigo_scad = parts[1].strip().replace("```scad", "").replace("```openscad", "").replace("```", "").strip()

        # CONVERSÃO SCAD PARA STL NO SERVIDOR
        stl_base64 = None
        scad_path = None
        stl_path = None

        try:
            with tempfile.NamedTemporaryFile(suffix=".scad", delete=False) as f_scad:
                f_scad.write(codigo_scad.encode('utf-8'))
                scad_path = f_scad.name
            
            stl_path = scad_path.replace(".scad", ".stl")
            
            # Compila o STL
            subprocess.run(["openscad", "-o", stl_path, scad_path], check=True, capture_output=True)
            
            # Converte para Base64
            with open(stl_path, "rb") as f_stl:
                stl_base64 = base64.b64encode(f_stl.read()).decode('utf-8')
                
        except Exception as conv_e:
            print(f"Erro na conversão STL: {conv_e}")
            stl_base64 = None
        finally:
            # Limpeza garantida de arquivos temporários
            if scad_path and os.path.exists(scad_path):
                os.remove(scad_path)
            if stl_path and os.path.exists(stl_path):
                os.remove(stl_path)

        return {
            "success": True,
            "justificativa": justificativa,
            "codigo_scad": codigo_scad,
            "stl_base64": stl_base64
        }
    except Exception as e:
        return {"success": False, "error": f"Erro ao processar modelo 3D: {str(e)}"}
