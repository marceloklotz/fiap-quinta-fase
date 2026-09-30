# 👩‍⚕️👨‍💻 Guardiã AI - Inteligência Artificial para Saúde e Segurança da Mulher: RAG (

[![FIAP Postech em IA para Devs](https://img.shields.io/badge/FIAP-Postech%20IA%20para%20Devs-blue?style=for-the-badge)](https://www.fiap.com.br/)
[![Fase 5 - Tech Challenge](https://img.shields.io/badge/Fase_5-Tech_Challenge-purple?style=for-the-badge)](https://github.com/marceloklotz/fiap-quinta-fase/)
[![RAG](https://img.shields.io/badge/RAG-green?style=for-the-badge)](#)

Esta pasta contem o script que extrai todos os Protocolos Clínicos e Diretrizes Terapêuticas (PCDTs) contidos no portal do Ministério da Saúde (https://www.gov.br/saude/pt-br/assuntos/pcdt) foi **disponibilizado em notebook separado** no repositório desse projeto e pode ser baixado pelo seguinte endereço: https://github.com/marceloklotz/fiap-quinta-fase/blob/main/PCDTs.ipynb

O código realiza a compactação dos protocolos disponibilizados originalmente em PDF, exporta para ZIP, além de converter, enriquecer e transformar em arquivos tipo *markdown*. O notebook contém a implementação completa do RAG com a extração, carregamento dos documentos, possibilitando a recuperação dos trechos relevantes e a inserção desses trechos neste notebook.

Resumo do fluxo para etapas utilizadas no PCDTs.ipynb:

*   📥 Crawler e Downloader
*   📦 Compactação e Download
*   ⚙️ Instalação das dependências (Célula de Código)
*   🔄 Conversão, Enriquecimento e Fragmentação (Célula de Código)
*   💾 Download dos Markdowns processados

O arquivo ZIP contendo os arquivos markdown dos "PCDTs" foi disponibilizado no seguinte link: https://github.com/marceloklotz/fiap-quinta-fase/blob/main/PCDTs_Markdown.zip

=> Além disso, foi disponibilizado o script (https://github.com/marceloklotz/fiap-quinta-fase/tree/main/Multilingual-E5-base) utilizado para executar localmente com SentenceTransformers para executar o FAISS (Facebook AI Similarity Search):

## 🚀 RAG Incremental Local/Offline com FAISS e Checkpoint

O script (https://github.com/marceloklotz/fiap-quinta-fase/tree/main/Multilingual-E5-base)  implementa um pipeline robusto e **incremental** para processamento e vetorização local de documentos (PCDTs) utilizando o modelo de embeddings multilíngue `intfloat/multilingual-e5-base` e o banco vetorial **FAISS**.

### ⚙️ Principais Funcionalidades Implementadas
* **Processamento Incremental Inteligente:** Detecta automaticamente arquivos novos, alterados ou removidos através de hashes SHA-256.
* **Evita Reprocessamento:** Identifica individualmente os chunks existentes para garantir que apenas o conteúdo novo ou modificado seja vetorizado.
* **Resiliência e Checkpoints:** Salva o progresso e o índice vetorial por lotes, permitindo a recuperação automática após interrupções e falhas locais.
* **Gerenciamento de Contexto:** Remove automaticamente chunks antigos pertencentes a documentos modificados ou excluídos.
* **Sincronização e Disponibilidade:** Prepara e valida o espaço vetorial configurando o `retriever` local pronto para uso imediato no RAG.

💡 **Nota sobre Arquitetura RAG (Retrieval-Augmented Generation):** Embora os documentos de referência (neste caso, os protocolos do Ministério da Saúde) estejam armazenados e sejam acessados via Google Drive (em vez de uma API ou banco de dados externo em tempo real), a arquitetura implementada configura o RAG ao buscar (retrieval) informações relevantes (chunks) em uma base de conhecimento externa ao modelo fundacional (os nossos PDFs vetorizados com FAISS), além de injetar esses trechos recuperados no prompt como contexto para o LLM gerar a resposta.
