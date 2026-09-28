# Etapa 3.1 — RAG incremental local/offline

Esta versão preserva a lógica da Etapa 3 original e substitui somente o backend de embeddings Gemini por `intfloat/multilingual-e5-base`, executado localmente com SentenceTransformers.

## O que permanece

- FAISS
- SHA-256 dos PCDTs
- fingerprint individual dos chunks
- detecção de PCDTs novos, alterados e removidos
- remoção dos chunks antigos de PCDTs alterados/removidos
- checkpoint por lote
- salvamento do FAISS após cada lote
- manifesto atualizado somente após conclusão
- registro de erro
- retry
- recuperação após interrupção
- retriever `k=4`
- sincronização opcional para uma pasta local do Google Drive para computador

## O que muda

`GoogleGenerativeAIEmbeddings` deixa de ser utilizado.

O embedding passa a ser gerado localmente pelo:

`intfloat/multilingual-e5-base`

O modelo suporta 94 idiomas e produz embeddings de 768 dimensões. O adaptador aplica `passage:` aos documentos e `query:` às consultas, mantendo o espaço semântico consistente.

## Importante sobre "100% offline"

Na primeira instalação, o modelo precisa ser baixado uma vez do Hugging Face, salvo localmente. Depois disso, o processamento da Etapa 3.1 não usa Gemini, Google API ou internet.

Para uma execução estritamente sem internet desde o primeiro processamento, baixe previamente o modelo para uma pasta local e configure `CAMINHO_MODELO_LOCAL` no `.env`.

## FAISS antigo

Não misture o FAISS criado com `gemini-embedding-001` com o novo FAISS E5.

Por padrão, esta versão usa:

`C:\RAG_PCDT\PCDT_FAISS_E5`

Ela também grava `embedding_config.json` e valida o modelo/dimensão antes de carregar um índice existente.

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
