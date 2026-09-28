import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

model_name = os.getenv("MODELO_EMBEDDING", "intfloat/multilingual-e5-base")
model_path = os.getenv("CAMINHO_MODELO_LOCAL", "").strip()

source = model_path if model_path else model_name

print(f"Baixando/preparando modelo: {source}")
model = SentenceTransformer(source)
print("Modelo pronto.")
print("Se desejar execução totalmente sem internet, informe uma pasta local em CAMINHO_MODELO_LOCAL.")
