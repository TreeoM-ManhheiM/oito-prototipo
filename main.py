import os
import base64
from fastapi import FastAPI, UploadFile, File
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

# Inicia o cliente da API do Groq utilizando a nova chave configurada no Render
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

# ROTA 1: Auditoria de Fotos de Anúncios com o CDC (Técnico em Vendas)
@app.post("/analyze-image")
async def analyze_image_endpoint(image: UploadFile = File(...)):
    image_bytes = await image.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    ext = image.filename.split(".")[-1].lower()
    mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

    system_prompt = """
    Você é um Auditor Jurídico e Professor Coordenador do curso Técnico em Vendas, especialista em Código de Defesa do Consumidor (CDC) aplicado ao Marketing Comercial.
    Sua função é analisar a imagem de um anúncio, panfleto, cartaz ou propaganda enviada pelos estudantes e emitir um relatório de conformidade legal rígido.
    
    Sua resposta DEVE ser dividida estritamente usando as marcações [TEXTO_CHAT] e [AUDIO_PROFESSOR].

    [TEXTO_CHAT]
    Crie um relatório estruturado em formato de Folha de Auditoria Comercial Oficial:
    
    1. PERCENTUAL DE ADERÊNCIA À LEI: Diga claramente a porcentagem estimada de quanto o anúncio cumpre as regras do CDC (Ex: "Porcentagem de Conformidade: 45%").
    2. O QUE FALTA / IRREGULARIDADES: Liste em tópicos curtos o que está errado ou ausente no anúncio (Falta de preço à vista, letras ilegíveis, indução a erro, etc.).
    3. ARTIGOS DO CDC VIOLADOS: Cite explicitamente os artigos correspondentes às infrações (Artigos 30, 31, 35, 36 e 37).
    4. RECOMENDAÇÃO TÉCNICA (SUGESTÃO DO VENDEDOR): Explique como os alunos de vendas devem reestruturar essa peça para que ela seja ética e legalizada.

    [AUDIO_PROFESSOR]
    Escreva EXCLUSIVAMENTE o texto que será narrado no ouvido do estudante. O tom deve ser de um professor avaliador analisando o trabalho do aluno em sala.
    - Comece de forma direta: "Analisando essa imagem que você mandou, a peça publicitária atingiu tantos por cento de conformidade com o nosso Código de Defesa do Consumidor."
    - Explique de forma conversacional qual foi o pior erro e o que eles devem corrigir. Proibido usar asteriscos ou emojis nesta seção de áudio.
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": system_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            model="llama-4-scout-17b-16e-instruct", # Atualizado para o modelo ativo com suporte visual
        )
        full_response = chat_completion.choices[0].message.content

        chat_text = "Não foi possível estruturar o relatório visual."
        audio_text = "Não foi possível estruturar o áudio."

        if "[AUDIO_PROFESSOR]" in full_response:
            parts = full_response.split("[AUDIO_PROFESSOR]")
            audio_text = parts[1].strip()
            chat_text = parts[0].replace("[TEXTO_CHAT]", "").strip()
        else:
            chat_text = full_response

        return {
            "teacher_response_chat": chat_text,
            "teacher_response_audio": audio_text
        }
    except Exception as e:
        return {"teacher_response_chat": f"Erro no processamento visual: {str(e)}", "teacher_response_audio": "Erro interno."}

# ROTA 2: Gerador de Códigos de MVP 3D (Inovação e Empreendedorismo)
@app.post("/generate-mvp")
async def generate_mvp_endpoint(request: MvpRequest):
    prompt_limpo = request.user_prompt.lower()
    
    # Validação prévia da lista negra da SEDUC
    if any(termo in prompt_limpo for termo in TERMOS_PROIBIDOS):
        return {
            "teacher_response_chat": "🚨 ALERTA DE SEGURANÇA: O pedido contém termos inadequados ou que violam as diretrizes do ambiente escolar.",
            "teacher_response_audio": "Atenção! Seu pedido foi bloqueado por violar as regras de segurança do laboratório."
        }
    
    system_prompt = """
    Você é o Engenheiro de Prototipagem Digital da ementa de Inovação e Empreendedorismo da SEDUC.
    Sua função é receber o pedido de um aluno para o MVP ou brinde da startup dele e gerar o código de modelagem programática em formato OpenSCAD que possa ser exportado para um arquivo STL para impressão 3D.

    REGRA DE CONTEXTO COMERCIAL:
    Se o aluno pedir um objeto que claramente NÃO possui finalidade comercial ou pedagógica para a grade (como personagens de jogos, espadas de brinquedo, etc.), você DEVE recusar a geração. Em vez do código, escreva uma mensagem curta pedindo para ele justificar a aplicação de negócios da peça.

    Sua resposta DEVE ser dividida estritamente usando as marcações [TEXTO_CHAT] e [AUDIO_PROFESSOR].

    [TEXTO_CHAT]
    Crie uma seção explicativa técnica seguida do bloco de código OpenSCAD limpo:
    1. JUSTIFICATIVA DO PROTÓTIPO: Uma frase dizendo como esse objeto ajuda no MVP da empresa.
    2. CÓDIGO OPENSCAD: Forneça o código OpenSCAD completo usando geometrias sólidas e limpas (cube, cylinder, sphere, union, difference). Mantenha as proporções em milímetros adequadas para uma mesa de impressão (limite de 100mm).

    [AUDIO_PROFESSOR]
    Escreva de forma conversacional o feedback para o aluno: "Muito bem, analisei a sua ideia de negócio e criei o modelo tridimensional do seu protótipo. O código OpenSCAD está pronto na sua prancheta para ser exportado e impresso em 3D."
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_prompt}
            ],
            model="llama-4-scout-17b-16e-instruct",
            temperature=0.2
        )
        full_response = chat_completion.choices[0].message.content

        chat_text = "Não foi possível gerar a malha geométrica."
        audio_text = "Não foi possível estruturar o áudio."

        if "[AUDIO_PROFESSOR]" in full_response:
            parts = full_response.split("[AUDIO_PROFESSOR]")
            audio_text = parts[1].strip()
            chat_text = parts[0].replace("[TEXTO_CHAT]", "").strip()
        else:
            chat_text = full_response

        return {
            "teacher_response_chat": chat_text,
            "teacher_response_audio": audio_text
        }
    except Exception as e:
        return {"teacher_response_chat": f"Erro ao processar modelo 3D: {str(e)}", "teacher_response_audio": "Erro no motor 3D."}