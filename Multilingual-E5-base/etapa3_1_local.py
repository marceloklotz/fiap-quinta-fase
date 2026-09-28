# ============================================================
# ETAPA 3.1 - RAG INCREMENTAL LOCAL/OFFLINE COM FAISS + CHECKPOINT
# ============================================================
#
# Recursos:
#
#   ✓ Recuperação do FAISS existente
#   ✓ Recuperação de processamento interrompido
#   ✓ Processamento incremental por PCDT
#   ✓ Detecção de arquivos novos
#   ✓ Detecção de arquivos alterados
#   ✓ Detecção de arquivos removidos
#   ✓ Hash SHA-256
#   ✓ Identificação individual dos chunks
#   ✓ Não reprocessa chunks já existentes
#   ✓ Checkpoint persistente por lote
#   ✓ Salvamento do FAISS após cada lote
#   ✓ Manifesto atualizado somente após conclusão
#   ✓ Retry para falhas transitórias do processamento local
#   ✓ Registro do último erro
#   ✓ Retry com espera progressiva
#   ✓ Continuação após interrupção do Windows/local
#   ✓ Retriever pronto ao final
#
# Estrutura:
#
# /MyDrive/PCDTs/
#       └── arquivos .md
#
# /MyDrive/PCDT_FAISS/
#       ├── index.faiss
#       ├── index.pkl
#       ├── manifest.json
#       └── checkpoint.json
#
# ============================================================

import os
import re
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime

from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np

from langchain_community.vectorstores import FAISS


# ============================================================
# 1. CONFIGURAÇÕES
# ============================================================

load_dotenv()

# Diretório-base local. Pode ser alterado por variável de ambiente.
CAMINHO_BASE = Path(
    os.getenv(
        "RAG_BASE_DIR",
        r"C:\RAG_PCDT"
    )
).expanduser()

CAMINHO_PCDT = str(
    Path(
        os.getenv(
            "RAG_PCDT_DIR",
            str(CAMINHO_BASE / "PCDTs")
        )
    ).expanduser()
)

CAMINHO_FAISS = str(
    Path(
        os.getenv(
            "RAG_FAISS_DIR",
            str(CAMINHO_BASE / "PCDT_FAISS_E5")
        )
    ).expanduser()
)

CAMINHO_DRIVE = os.getenv(
    "GOOGLE_DRIVE_FAISS_DIR",
    ""
)

CAMINHO_MANIFEST = os.path.join(
    CAMINHO_FAISS,
    "manifest.json"
)

CAMINHO_CHECKPOINT = os.path.join(
    CAMINHO_FAISS,
    "checkpoint.json"
)

CAMINHO_ERRO = os.path.join(
    CAMINHO_FAISS,
    "ultimo_erro.json"
)

CAMINHO_CONFIG_EMBEDDING = os.path.join(
    CAMINHO_FAISS,
    "embedding_config.json"
)

# Modelo local multilíngue. Após o primeiro download,
# a execução da Etapa 3.1 não depende de API externa.
MODELO_EMBEDDING = os.getenv(
    "MODELO_EMBEDDING",
    "intfloat/multilingual-e5-base"
)

CAMINHO_MODELO_LOCAL = os.getenv(
    "CAMINHO_MODELO_LOCAL",
    ""
)

DISPOSITIVO_EMBEDDING = os.getenv(
    "EMBEDDING_DEVICE",
    "auto"
)

EMBEDDING_BATCH_SIZE = int(
    os.getenv(
        "EMBEDDING_BATCH_SIZE",
        "16"
    )
)

CHUNK_SIZE = 1500

CHUNK_OVERLAP = 150

TOP_K = 4

BATCH_SIZE = 20

MAX_RETRIES = 3

PAUSA_ENTRE_LOTES = 1


os.makedirs(
    CAMINHO_FAISS,
    exist_ok=True
)


print("=" * 70)
print("🚀 ETAPA 3.1 - RAG INCREMENTAL LOCAL/OFFLINE")
print("=" * 70)
print()
print("Modelo:", MODELO_EMBEDDING)
print("PCDTs :", CAMINHO_PCDT)
print("FAISS :", CAMINHO_FAISS)
print()


# ============================================================
# 2. HASH DO ARQUIVO
# ============================================================

def calcular_hash_arquivo(caminho):

    sha256 = hashlib.sha256()

    with open(caminho, "rb") as arquivo:

        while True:

            bloco = arquivo.read(
                1024 * 1024
            )

            if not bloco:
                break

            sha256.update(bloco)

    return sha256.hexdigest()


# ============================================================
# 3. HASH DO CHUNK
# ============================================================

def calcular_hash_chunk(
    arquivo_pcdt,
    hash_pcdt,
    numero_chunk,
    conteudo
):

    texto = (
        f"{arquivo_pcdt}|"
        f"{hash_pcdt}|"
        f"{numero_chunk}|"
        f"{conteudo}"
    )

    return hashlib.sha256(
        texto.encode("utf-8")
    ).hexdigest()


# ============================================================
# 4. OBTÉM MANIFESTO ATUAL
# ============================================================

def obter_manifesto_atual():

    manifesto = {}

    caminho_base = Path(
        CAMINHO_PCDT
    )

    if not caminho_base.exists():

        raise FileNotFoundError(
            f"O diretório de PCDTs não existe:\n"
            f"{CAMINHO_PCDT}"
        )

    arquivos = sorted(
        caminho_base.rglob("*.md")
    )

    if not arquivos:

        raise FileNotFoundError(
            f"Nenhum arquivo .md encontrado em:\n"
            f"{CAMINHO_PCDT}"
        )

    print(
        f"📄 Arquivos Markdown encontrados: "
        f"{len(arquivos)}"
    )

    for caminho in arquivos:

        caminho = caminho.resolve()

        nome_relativo = str(
            caminho.relative_to(
                caminho_base.resolve()
            )
        )

        manifesto[nome_relativo] = {

            "hash": calcular_hash_arquivo(
                str(caminho)
            ),

            "tamanho": caminho.stat().st_size,

            "arquivo": nome_relativo
        }

    return manifesto


# ============================================================
# 5. CARREGA JSON
# ============================================================

def carregar_json(caminho):

    if not os.path.exists(caminho):

        return None

    try:

        with open(
            caminho,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(
                arquivo
            )

    except Exception as erro:

        print(
            f"⚠️ Erro ao carregar "
            f"{caminho}: {erro}"
        )

        return None


# ============================================================
# 6. SALVA JSON DE FORMA SEGURA
# ============================================================

def salvar_json_seguro(
    caminho,
    dados
):

    caminho_temporario = (
        caminho + ".tmp"
    )

    with open(
        caminho_temporario,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            dados,
            arquivo,
            ensure_ascii=False,
            indent=2
        )

    os.replace(
        caminho_temporario,
        caminho
    )


# ============================================================
# 7. MANIFESTO
# ============================================================

manifesto_atual = (
    obter_manifesto_atual()
)

manifesto_anterior = (
    carregar_json(
        CAMINHO_MANIFEST
    )
)


# ============================================================
# 8. COMPARAÇÃO DOS MANIFESTOS
# ============================================================

if manifesto_anterior is None:

    arquivos_novos = sorted(
        manifesto_atual.keys()
    )

    arquivos_alterados = []

    arquivos_removidos = []

    arquivos_inalterados = []

else:

    conjunto_anterior = set(
        manifesto_anterior.keys()
    )

    conjunto_atual = set(
        manifesto_atual.keys()
    )

    arquivos_novos = sorted(
        conjunto_atual -
        conjunto_anterior
    )

    arquivos_removidos = sorted(
        conjunto_anterior -
        conjunto_atual
    )

    arquivos_alterados = []

    arquivos_inalterados = []

    for arquivo in sorted(
        conjunto_atual &
        conjunto_anterior
    ):

        hash_anterior = (
            manifesto_anterior[
                arquivo
            ]["hash"]
        )

        hash_atual = (
            manifesto_atual[
                arquivo
            ]["hash"]
        )

        if hash_anterior == hash_atual:

            arquivos_inalterados.append(
                arquivo
            )

        else:

            arquivos_alterados.append(
                arquivo
            )


print()
print("=" * 70)
print("🔎 ALTERAÇÕES DETECTADAS")
print("=" * 70)

print(
    f"➕ Novos:        {len(arquivos_novos)}"
)

print(
    f"✏️ Alterados:    {len(arquivos_alterados)}"
)

print(
    f"➖ Removidos:    {len(arquivos_removidos)}"
)

print(
    f"✅ Inalterados:  {len(arquivos_inalterados)}"
)

print()


# ============================================================
# 9. VERIFICA FAISS EXISTENTE
# ============================================================

ARQUIVO_FAISS = os.path.join(
    CAMINHO_FAISS,
    "index.faiss"
)

ARQUIVO_PKL = os.path.join(
    CAMINHO_FAISS,
    "index.pkl"
)

FAISS_EXISTENTE = (

    os.path.exists(
        ARQUIVO_FAISS
    )

    and

    os.path.exists(
        ARQUIVO_PKL
    )
)


# ============================================================
# 10. CRIA OBJETO DE EMBEDDINGS
# ============================================================

# ============================================================
# 10. MODELO DE EMBEDDINGS LOCAL
# ============================================================

class E5Embeddings(Embeddings):
    """
    Adaptador LangChain para o intfloat/multilingual-e5-base.

    O E5 utiliza prefixos diferentes para documentos e consultas:
      passage: texto do PCDT
      query: texto da consulta
    """

    def __init__(
        self,
        model_name,
        model_path="",
        device="auto",
        batch_size=16
    ):
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except Exception:
                device = "cpu"

        origem = model_path.strip() if model_path else model_name

        print(
            f"🧠 Carregando embedding local: {origem}"
        )
        print(
            f"🖥️ Dispositivo: {device}"
        )

        self.model_name = model_name
        self.model_path = origem
        self.device = device
        self.batch_size = batch_size

        self.model = SentenceTransformer(
            origem,
            device=device
        )

    def _encode(self, textos):
        if not textos:
            return []

        preparados = [
            texto if texto.startswith(("query: ", "passage: "))
            else f"passage: {texto}"
            for texto in textos
        ]

        vetores = self.model.encode(
            preparados,
            batch_size=self.batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        return vetores.astype(np.float32).tolist()

    def embed_documents(self, texts):
        return self._encode(
            [f"passage: {texto}" for texto in texts]
        )

    def embed_query(self, text):
        vetor = self.model.encode(
            f"query: {text}",
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )

        return vetor.astype(np.float32).tolist()


print(
    "🧠 Inicializando modelo de embeddings local..."
)

embeddings = E5Embeddings(
    model_name=MODELO_EMBEDDING,
    model_path=CAMINHO_MODELO_LOCAL,
    device=DISPOSITIVO_EMBEDDING,
    batch_size=EMBEDDING_BATCH_SIZE
)

# Configuração do embedding usada neste índice.
CONFIG_EMBEDDING = {
    "modelo": MODELO_EMBEDDING,
    "caminho_modelo_local": CAMINHO_MODELO_LOCAL,
    "dimensao": len(embeddings.embed_query("teste")),
    "normalizacao": True,
    "familia": "multilingual-e5",
    "versao_etapa": "3.1"
}

# Registra a identidade do espaço vetorial antes de qualquer
# gravação do FAISS. Isso permite recuperar uma execução
# interrompida sem misturar modelos incompatíveis.
if not os.path.exists(CAMINHO_CONFIG_EMBEDDING):
    salvar_json_seguro(
        CAMINHO_CONFIG_EMBEDDING,
        CONFIG_EMBEDDING
    )



# ============================================================
# 11. CARREGA FAISS EXISTENTE
# ============================================================

vectorstore = None

if FAISS_EXISTENTE:

    config_existente = carregar_json(
        CAMINHO_CONFIG_EMBEDDING
    )

    if not config_existente:
        raise RuntimeError(
            "O FAISS existente não possui embedding_config.json. "
            "Ele pode ter sido criado com outro modelo (por exemplo, Gemini). "
            "Use um diretório FAISS novo para a Etapa 3.1."
        )

    modelo_existente = config_existente.get("modelo")
    dimensao_existente = config_existente.get("dimensao")
    dimensao_atual = CONFIG_EMBEDDING["dimensao"]

    if modelo_existente != MODELO_EMBEDDING:
        raise RuntimeError(
            f"Incompatibilidade de embeddings: FAISS={modelo_existente} "
            f"| atual={MODELO_EMBEDDING}. "
            "Não é permitido misturar espaços vetoriais diferentes."
        )

    if dimensao_existente != dimensao_atual:
        raise RuntimeError(
            f"Incompatibilidade de dimensão: FAISS={dimensao_existente} "
            f"| atual={dimensao_atual}."
        )

    print()
    print(
        "♻️ FAISS existente encontrado."
    )

    try:

        vectorstore = FAISS.load_local(

            CAMINHO_FAISS,

            embeddings,

            allow_dangerous_deserialization=True
        )

        print(
            "✅ FAISS carregado."
        )

        try:

            print(
                f"📊 Vetores atualmente no FAISS: "
                f"{vectorstore.index.ntotal}"
            )

        except Exception:

            pass

    except Exception as erro:

        print()
        print(
            "❌ Não foi possível carregar "
            "o FAISS existente."
        )

        print(
            f"Erro: {erro}"
        )

        raise

else:

    print(
        "ℹ️ Nenhum FAISS existente encontrado."
    )

    print(
        "🆕 Será criado um novo índice."
    )


# ============================================================
# 12. CONSTRÓI MAPA DOS CHUNKS JÁ EXISTENTES
# ============================================================
#
# Esta parte é fundamental para recuperar o que já foi
# processado, inclusive o FAISS salvo pela execução anterior.
#
# O código não depende apenas do checkpoint.
# Ele também verifica o conteúdo efetivamente existente
# dentro do FAISS.
# ============================================================

chunks_existentes = {}

if vectorstore is not None:

    print()
    print(
        "🔍 Analisando chunks existentes no FAISS..."
    )

    try:

        docstore = (
            vectorstore.docstore._dict
        )

        for id_documento, doc in (
            docstore.items()
        ):

            metadata = (
                doc.metadata or {}
            )

            arquivo = metadata.get(
                "arquivo_pcdt"
            )

            hash_pcdt = metadata.get(
                "hash_pcdt"
            )

            if not arquivo:

                continue

            conteudo = (
                doc.page_content or ""
            )

            # ------------------------------------------------
            # Compatibilidade com o índice antigo.
            #
            # Como o código anterior não armazenava
            # explicitamente o número do chunk, criamos
            # uma identificação baseada no conteúdo.
            # ------------------------------------------------

            fingerprint = hashlib.sha256(
                (
                    f"{arquivo}|"
                    f"{hash_pcdt}|"
                    f"{conteudo}"
                ).encode("utf-8")
            ).hexdigest()

            chunks_existentes[
                fingerprint
            ] = {

                "id": id_documento,

                "arquivo": arquivo,

                "hash": hash_pcdt,

                "conteudo": conteudo
            }

        print(
            f"✅ Chunks identificados no FAISS: "
            f"{len(chunks_existentes)}"
        )

    except Exception as erro:

        print(
            "⚠️ Não foi possível analisar "
            f"todos os chunks existentes: {erro}"
        )


# ============================================================
# 13. FUNÇÃO PARA CARREGAR PCDTs
# ============================================================

def carregar_documentos():

    loader = DirectoryLoader(

        CAMINHO_PCDT,

        glob="**/*.md",

        loader_cls=TextLoader,

        loader_kwargs={
            "encoding": "utf-8"
        }
    )

    documentos = loader.load()

    if not documentos:

        raise ValueError(
            "Nenhum documento PCDT foi carregado."
        )

    return documentos


# ============================================================
# 14. PREPARA DOCUMENTOS
# ============================================================

documentos = carregar_documentos()

print()
print(
    f"📚 Documentos carregados: "
    f"{len(documentos)}"
)


caminho_base = Path(
    CAMINHO_PCDT
).resolve()


for doc in documentos:

    # --------------------------------------------------------
    # Portaria
    # --------------------------------------------------------

    texto_limpo = (
        doc.page_content
        .replace("*", "")
    )

    match = re.search(

        r"(PORTARIA\s+N[º°]?\s*"
        r"[\d\.\/-]+\s+DE\s+.*?\d{4})",

        texto_limpo,

        re.IGNORECASE
    )

    if match:

        doc.metadata[
            "portaria"
        ] = (
            match.group(1)
            .strip()
            .upper()
        )

    else:

        doc.metadata[
            "portaria"
        ] = (
            "Portaria não informada no documento"
        )

    # --------------------------------------------------------
    # Arquivo e hash
    # --------------------------------------------------------

    caminho_origem = (
        doc.metadata.get(
            "source"
        )
    )

    if caminho_origem:

        caminho_origem = (
            Path(caminho_origem)
            .resolve()
        )

        nome_relativo = str(
            caminho_origem.relative_to(
                caminho_base
            )
        )

        doc.metadata[
            "arquivo_pcdt"
        ] = nome_relativo

        if nome_relativo in manifesto_atual:

            doc.metadata[
                "hash_pcdt"
            ] = manifesto_atual[
                nome_relativo
            ]["hash"]


# ============================================================
# 15. SEPARA DOCUMENTOS QUE PRECISAM SER PROCESSADOS
# ============================================================

arquivos_para_processar = sorted(
    set(
        arquivos_novos +
        arquivos_alterados
    )
)

print()
print("=" * 70)
print("📋 PCDTs QUE NECESSITAM DE PROCESSAMENTO")
print("=" * 70)

if arquivos_para_processar:

    for arquivo in arquivos_para_processar:

        if arquivo in arquivos_novos:

            print(
                f"➕ NOVO     : {arquivo}"
            )

        else:

            print(
                f"✏️ ALTERADO : {arquivo}"
            )

else:

    print(
        "✅ Nenhum PCDT novo ou alterado."
    )


# ============================================================
# 16. REMOVE CHUNKS DE PCDTs ALTERADOS OU REMOVIDOS
# ============================================================
#
# Para um PCDT alterado:
#
#   versão antiga → removida
#   versão nova   → processada
#
# Isso evita manter simultaneamente duas versões do mesmo PCDT.
# ============================================================

arquivos_para_limpar = set(
    arquivos_alterados +
    arquivos_removidos
)


if (
    vectorstore is not None
    and arquivos_para_limpar
):

    print()
    print(
        "🧹 Verificando chunks antigos "
        "de PCDTs alterados/removidos..."
    )

    ids_para_remover = []

    try:

        docstore = (
            vectorstore.docstore._dict
        )

        for id_documento, doc in (
            docstore.items()
        ):

            arquivo = (
                doc.metadata.get(
                    "arquivo_pcdt"
                )
                if doc.metadata
                else None
            )

            if arquivo in arquivos_para_limpar:

                ids_para_remover.append(
                    id_documento
                )

        if ids_para_remover:

            print(
                f"🗑️ Removendo "
                f"{len(ids_para_remover)} "
                f"chunks antigos..."
            )

            vectorstore.delete(
                ids_para_remover
            )

            # Reconstroi o mapa
            chunks_existentes = {}

            docstore = (
                vectorstore.docstore._dict
            )

            for id_documento, doc in (
                docstore.items()
            ):

                metadata = (
                    doc.metadata or {}
                )

                arquivo = metadata.get(
                    "arquivo_pcdt"
                )

                hash_pcdt = metadata.get(
                    "hash_pcdt"
                )

                if not arquivo:

                    continue

                conteudo = (
                    doc.page_content or ""
                )

                fingerprint = hashlib.sha256(
                    (
                        f"{arquivo}|"
                        f"{hash_pcdt}|"
                        f"{conteudo}"
                    ).encode("utf-8")
                ).hexdigest()

                chunks_existentes[
                    fingerprint
                ] = {

                    "id": id_documento,

                    "arquivo": arquivo,

                    "hash": hash_pcdt,

                    "conteudo": conteudo
                }

            # Salva imediatamente após limpeza
            vectorstore.save_local(
                CAMINHO_FAISS
            )

            print(
                "✅ Chunks antigos removidos "
                "e FAISS salvo."
            )

        else:

            print(
                "ℹ️ Nenhum chunk antigo "
                "precisou ser removido."
            )

    except Exception as erro:

        print(
            f"⚠️ Erro ao remover chunks antigos: "
            f"{erro}"
        )

        raise


# ============================================================
# 17. DIVISÃO DOS DOCUMENTOS EM CHUNKS
# ============================================================

text_splitter = (
    RecursiveCharacterTextSplitter(

        chunk_size=CHUNK_SIZE,

        chunk_overlap=CHUNK_OVERLAP,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )
)


# ============================================================
# 18. GERA SOMENTE OS CHUNKS NECESSÁRIOS
# ============================================================

chunks_pendentes = []


for doc in documentos:

    arquivo = doc.metadata.get(
        "arquivo_pcdt"
    )

    hash_pcdt = doc.metadata.get(
        "hash_pcdt"
    )

    # --------------------------------------------------------
    # Se o arquivo não é novo nem alterado e já está no índice,
    # não precisamos gerar seus chunks novamente.
    # --------------------------------------------------------

    if (
        arquivo not in arquivos_para_processar
    ):

        continue

    splits = text_splitter.split_documents(
        [doc]
    )

    print()
    print(
        f"📄 {arquivo}"
    )

    print(
        f"   🧩 Chunks gerados: "
        f"{len(splits)}"
    )

    for numero_chunk, chunk in enumerate(
        splits
    ):

        conteudo = (
            chunk.page_content or ""
        )

        fingerprint = hashlib.sha256(
            (
                f"{arquivo}|"
                f"{hash_pcdt}|"
                f"{conteudo}"
            ).encode("utf-8")
        ).hexdigest()

        # ----------------------------------------------------
        # Se o chunk já existe, NÃO gera embedding novamente.
        # ----------------------------------------------------

        if fingerprint in chunks_existentes:

            continue

        chunk.metadata[
            "arquivo_pcdt"
        ] = arquivo

        chunk.metadata[
            "hash_pcdt"
        ] = hash_pcdt

        chunk.metadata[
            "chunk_numero"
        ] = numero_chunk

        chunk.metadata[
            "chunk_fingerprint"
        ] = fingerprint

        chunks_pendentes.append(
            chunk
        )


print()
print("=" * 70)
print("📊 RESUMO DO PROCESSAMENTO")
print("=" * 70)

print(
    f"📚 PCDTs novos/alterados : "
    f"{len(arquivos_para_processar)}"
)

print(
    f"🧩 Chunks que faltam     : "
    f"{len(chunks_pendentes)}"
)

if vectorstore is not None:

    try:

        print(
            f"💾 Vetores já no FAISS  : "
            f"{vectorstore.index.ntotal}"
        )

    except Exception:

        pass

print()


# ============================================================
# 19. CHECKPOINT
# ============================================================

checkpoint = carregar_json(
    CAMINHO_CHECKPOINT
)

if checkpoint is None:

    checkpoint = {

        "inicio": datetime.now().isoformat(),

        "modelo_embedding":
            MODELO_EMBEDDING,

        "arquivos_em_processamento":
            arquivos_para_processar,

        "chunks_concluidos": 0,

        "ultimo_lote": None,

        "ultima_atualizacao":
            datetime.now().isoformat()
    }


# ============================================================
# 20. FUNÇÃO PARA SALVAR CHECKPOINT
# ============================================================

def salvar_checkpoint(
    quantidade_concluida,
    ultimo_lote,
    status="em_andamento"
):

    dados = {

        "inicio": checkpoint.get(
            "inicio"
        ),

        "modelo_embedding":
            MODELO_EMBEDDING,

        "arquivos_em_processamento":
            arquivos_para_processar,

        "chunks_pendentes_inicial":
            len(chunks_pendentes),

        "chunks_concluidos":
            quantidade_concluida,

        "ultimo_lote":
            ultimo_lote,

        "status":
            status,

        "ultima_atualizacao":
            datetime.now().isoformat()
    }

    salvar_json_seguro(
        CAMINHO_CHECKPOINT,
        dados
    )


# ============================================================
# 21. FUNÇÃO PARA REGISTRAR ERRO
# ============================================================

def registrar_erro(
    erro,
    inicio_lote,
    fim_lote
):

    dados = {

        "data":
            datetime.now().isoformat(),

        "lote_inicio":
            inicio_lote,

        "lote_fim":
            fim_lote,

        "tipo":
            type(erro).__name__,

        "mensagem":
            str(erro)
    }

    salvar_json_seguro(
        CAMINHO_ERRO,
        dados
    )


# ============================================================
# 22. PROCESSAMENTO INCREMENTAL
# ============================================================

total_pendentes = (
    len(chunks_pendentes)
)


if total_pendentes == 0:

    print(
        "🎉 Nenhum embedding novo é necessário."
    )

else:

    print("=" * 70)
    print(
        "🧠 INICIANDO PROCESSAMENTO INCREMENTAL"
    )
    print("=" * 70)

    print(
        f"Total de chunks pendentes: "
        f"{total_pendentes}"
    )

    quantidade_concluida = 0

    for inicio in range(
        0,
        total_pendentes,
        BATCH_SIZE
    ):

        fim = min(
            inicio + BATCH_SIZE,
            total_pendentes
        )

        lote = chunks_pendentes[
            inicio:fim
        ]

        print()
        print("=" * 70)
        print(
            f"🔄 LOTE "
            f"{inicio + 1}–{fim} "
            f"de {total_pendentes}"
        )
        print("=" * 70)

        sucesso = False

        ultimo_erro = None

        for tentativa in range(
            MAX_RETRIES
        ):

            try:

                # ------------------------------------------------
                # Primeiro lote de um FAISS inexistente
                # ------------------------------------------------

                if vectorstore is None:

                    vectorstore = (
                        FAISS.from_documents(
                            lote,
                            embeddings
                        )
                    )

                else:

                    vectorstore.add_documents(
                        lote
                    )

                sucesso = True

                quantidade_concluida += len(
                    lote
                )

                print()
                print(
                    "   ✅ Lote processado."
                )

                # ------------------------------------------------
                # SALVAMENTO IMEDIATO
                # ------------------------------------------------

                print(
                    "   💾 Salvando checkpoint "
                    "do FAISS..."
                )

                vectorstore.save_local(
                    CAMINHO_FAISS
                )

                salvar_checkpoint(

                    quantidade_concluida,

                    {
                        "inicio":
                            inicio + 1,

                        "fim":
                            fim
                    },

                    status="em_andamento"
                )

                print(
                    "   ✅ Checkpoint salvo."
                )

                try:

                    print(
                        f"   📊 Vetores no FAISS: "
                        f"{vectorstore.index.ntotal}"
                    )

                except Exception:

                    pass

                break

            except Exception as erro:

                ultimo_erro = erro

                mensagem = str(
                    erro
                )

                registrar_erro(
                    erro,
                    inicio + 1,
                    fim
                )

                if (
                    "429" in mensagem
                    or
                    "RESOURCE_EXHAUSTED"
                    in mensagem
                ):

                    espera = min(

                        300,

                        30 * (
                            tentativa + 1
                        )
                    )

                    print()
                    print(
                        "   ⚠️ Falha no processamento local. "
                        "Tentando novamente."
                    )

                    print(
                        f"   Tentativa: "
                        f"{tentativa + 1}/"
                        f"{MAX_RETRIES}"
                    )

                    print(
                        f"   ⏳ Aguardando "
                        f"{espera} segundos..."
                    )

                    time.sleep(
                        espera
                    )

                else:

                    print()
                    print(
                        "   ❌ Erro não relacionado "
                        "diretamente à quota:"
                    )

                    print(
                        f"   {mensagem}"
                    )

                    raise

        if not sucesso:

            salvar_checkpoint(

                quantidade_concluida,

                {
                    "inicio":
                        inicio + 1,

                    "fim":
                        fim
                },

                status="interrompido_por_erro"
            )

            raise RuntimeError(

                f"\n"
                f"❌ O lote {inicio + 1}–{fim} "
                f"não pôde ser processado após "
                f"{MAX_RETRIES} tentativas.\n\n"

                f"Último erro:\n"
                f"{ultimo_erro}\n\n"

                f"💾 O FAISS e o checkpoint dos "
                f"lotes anteriores foram preservados.\n"

                f"▶️ Você poderá executar novamente "
                f"esta célula para continuar."
            )

        # --------------------------------------------------------
        # Pausa normal entre lotes
        # --------------------------------------------------------

        if fim < total_pendentes:

            time.sleep(
                PAUSA_ENTRE_LOTES
            )


# ============================================================
# 23. SALVA CONFIGURAÇÃO DO EMBEDDING
# ============================================================

salvar_json_seguro(
    CAMINHO_CONFIG_EMBEDDING,
    CONFIG_EMBEDDING
)

# ============================================================
# 24. SALVA FAISS FINAL
# ============================================================

if vectorstore is not None:

    print()
    print(
        "💾 Salvando estado final do FAISS..."
    )

    vectorstore.save_local(
        CAMINHO_FAISS
    )


# ============================================================
# 24. ATUALIZA MANIFESTO SOMENTE AGORA
# ============================================================
#
# Só chegamos aqui se todos os chunks pendentes
# tiverem sido processados.
# ============================================================

salvar_json_seguro(

    CAMINHO_MANIFEST,

    manifesto_atual
)


# ============================================================
# 25. CHECKPOINT FINAL
# ============================================================

salvar_checkpoint(

    total_pendentes,

    {
        "inicio": 1,
        "fim": total_pendentes
    },

    status="concluido"
)

# ============================================================
# SINCRONIZAÇÃO OPCIONAL COM GOOGLE DRIVE DESKTOP
# ============================================================

def sincronizar_com_google_drive():
    """
    Copia os artefatos finais para uma pasta local do Google Drive
    (Google Drive para computador). Não usa API/OAuth.
    """
    if not CAMINHO_DRIVE:
        print(
            "ℹ️ GOOGLE_DRIVE_FAISS_DIR não configurado. "
            "Sincronização ignorada."
        )
        return

    origem = Path(CAMINHO_FAISS)
    destino = Path(CAMINHO_DRIVE)
    destino.mkdir(parents=True, exist_ok=True)

    arquivos = [
        "index.faiss",
        "index.pkl",
        "manifest.json",
        "checkpoint.json",
        "ultimo_erro.json",
        "embedding_config.json"
    ]

    print(f"☁️ Sincronizando FAISS para: {destino}")

    import shutil

    for nome in arquivos:
        arquivo_origem = origem / nome
        if arquivo_origem.exists():
            destino_temp = destino / f"{nome}.tmp"
            destino_final = destino / nome

            shutil.copy2(
                arquivo_origem,
                destino_temp
            )
            os.replace(
                destino_temp,
                destino_final
            )

    print("✅ Sincronização concluída.")

sincronizar_com_google_drive()


# ============================================================
# 26. CRIA RETRIEVER
# ============================================================

if vectorstore is None:

    raise RuntimeError(
        "O VectorStore não foi criado."
    )


retriever = vectorstore.as_retriever(

    search_kwargs={
        "k": TOP_K
    }
)


# ============================================================
# 27. RESULTADO FINAL
# ============================================================

print()
print("=" * 70)
print("🎉 ETAPA 3.1 LOCAL CONCLUÍDA")
print("=" * 70)

print(
    f"📚 PCDTs encontrados: "
    f"{len(manifesto_atual)}"
)

print(
    f"➕ Novos: "
    f"{len(arquivos_novos)}"
)

print(
    f"✏️ Alterados: "
    f"{len(arquivos_alterados)}"
)

print(
    f"➖ Removidos: "
    f"{len(arquivos_removidos)}"
)

print(
    f"🧩 Chunks processados nesta execução: "
    f"{total_pendentes}"
)

try:

    print(
        f"💾 Total de vetores no FAISS: "
        f"{vectorstore.index.ntotal}"
    )

except Exception:

    pass

print(
    f"🧠 Modelo: "
    f"{MODELO_EMBEDDING}"
)

print(
    f"📏 Chunk size: "
    f"{CHUNK_SIZE}"
)

print(
    f"🔁 Overlap: "
    f"{CHUNK_OVERLAP}"
)

print(
    f"🔎 Top-K: "
    f"{TOP_K}"
)

print()
print(
    "💾 FAISS persistido localmente."
)

print(
    "📝 Manifesto atualizado."
)

print(
    "📝 Checkpoint atualizado."
)

print(
    "🚀 Retriever pronto para utilização pelo RAG."
)

print("=" * 70)