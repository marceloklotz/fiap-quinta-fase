# Usa uma imagem base leve do Python 3.10
FROM python:3.10-slim

# Instala o ffmpeg (crítico para a transcrição de áudio em MP3) e ferramentas de build
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de dependências e realiza a instalação sem gerar cache (otimização de RAM)
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia os arquivos locais para o contêiner
COPY . .

# Expõe a porta padrão do Jupyter
EXPOSE 8888

# Inicia o Jupyter Lab aberto para localhost sem token (ideal para desenvolvimento local rápido)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]