# RAG incremental local/offline

Este script utiliza o modelo Multilingual-E5-base (disponível no Hugging Face) em substituição a outros modelos de embeddings que foram utilizados no projeto (Gemini/OpenAI). O script é executado localmente com SentenceTransformers.

## Aprimoramentos realizados

- FAISS
- SHA-256 dos PCDTs
- fingerprint individual dos chunks
- detecção de arquivos de protocolos médicos (PCDTs) novos, alterados e removidos na base
- remoção dos chunks antigos de PCDTs alterados/removidos
- checkpoint por lote
- salvamento do FAISS após cada lote
- manifesto atualizado somente após conclusão
- registro de erro
- retry
- recuperação após interrupção
- retriever `k=4`
- sincronização opcional para uma pasta local do Google Drive para computador

## Outras alterações realizadas

`GoogleGenerativeAIEmbeddings` deixa de ser utilizado.

O embedding passa a ser gerado localmente pelo:

`intfloat/multilingual-e5-base`

O modelo suporta 94 idiomas e produz embeddings de 768 dimensões. O adaptador aplica `passage:` aos documentos e `query:` às consultas, mantendo o espaço semântico consistente.

## Nota

Na primeira instalação, o modelo precisa ser baixado uma vez do Hugging Face, salvo localmente. Depois disso, o processamento dos arquivos deixa de utilizar o Gemini, Google API ou internet.

Por padrão, esta versão usa o caminho (`C:\RAG_PCDT\PCDT_FAISS_E5`) e grava `embedding_config.json`, validando o modelo/dimensão antes de carregar um índice existente.

## Google Drive

A sincronização não usa API OAuth. Ela copia os arquivos para uma pasta local monitorada pelo Google Drive para computador:

- index.faiss
- index.pkl
- manifest.json
- checkpoint.json
- ultimo_erro.json
- embedding_config.json

O Google Drive faz a sincronização para a nuvem.

## Execução

1. Instale Python 3.11 ou 3.12.
2. Execute `instalar.ps1`.
3. Edite `.env`.
4. Coloque os PCDTs `.md` em `RAG_PCDT_DIR`.
5. Execute:

```powershell
.\.venv\Scripts\python.exe .\etapa3_1_local.py
```

Na primeira execução o modelo será baixado, salvo no cache do SentenceTransformers e utilizado localmente.

## Link para download no HuggingFace

https://huggingface.co/intfloat/multilingual-e5-base
