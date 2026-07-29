# Usa uma imagem oficial do Python leve
FROM python:3.10-slim

# Instala o OpenSCAD diretamente no sistema operacional do servidor
RUN apt-get update && \
    apt-get install -y openscad && \
    rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do seu GitHub para dentro do servidor
COPY . /app

# Instala as dependências do Python (FastAPI, Groq, etc)
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta padrão que o Render costuma utilizar
EXPOSE 10000

# Comando para iniciar sua aplicação FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
