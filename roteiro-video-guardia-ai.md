# Roteiro Técnico de Vídeo: Guardiã AI — Apresentação de Projeto Acadêmico (Tech Challenge - Fase 5)

## 1. Ficha Técnica e Diretrizes de Produção

* **Título do Projeto**: Guardiã AI — Inteligência Artificial para Saúde e Segurança da Mulher
* **Programa Acadêmico**: Pós-Tech FIAP (8IADT) — IA para Devs (Tech Challenge - Fase 5)
* **Equipe de Desenvolvimento**: Servidores da Secretaria de Segurança Pública do Distrito Federal (SSP/DF)
* **Duração Total do Vídeo**: 15 minutos (15:00)
* **Formato**: Vídeo demonstrativo técnico com alternância entre telas de apresentação, gravações de execução de código no Google Colab e VS Code, diagramas de arquitetura e locução/apresentação em câmera.
* **Público-Alvo**: Banca examinadora acadêmica, engenheiros de IA, profissionais de saúde e gestores de tecnologia pública.

---

## 2. Estrutura Cronológica do Roteiro

```
00:00 ─── 02:30 | Bloco 1: Visão Geral, Propósito e Arquitetura Multi-Provedor
02:30 ─── 05:00 | Bloco 2: Aquisição e Fragmentação de PCDTs (PCDTs.ipynb)
05:00 ─── 08:00 | Bloco 3: RAG Incremental Local e Indexação FAISS (etapa3_1_local.py)
08:00 ─── 11:00 | Bloco 4: Notebook Principal — Triagem XGBoost/SHAP e Biomarcadores Vocais
11:00 ─── 14:00 | Bloco 5: Transcrição Whisper, RAG Multiconsulta e Violência Doméstica
14:00 ─── 15:00 | Bloco 6: Relatório SOAP, Validação, Ética e Encerramento
```

---

## 3. Detalhamento Bloco a Bloco

### Bloco 1: Visão Geral, Propósito e Arquitetura Multi-Provedor (00:00 – 02:30)

* **Duração**: 2 minutos e 30 segundos
* **Objetivo**: Apresentar o problema clínico e social, os objetivos do projeto e o diagrama arquitetural da solução com suporte multi-provedor.

#### Orientação de Cena e Recursos Visuais
* **[00:00 – 00:30]**: Tela cheia com a marca oficial do Guardiã AI e identificação dos integrantes da SSP/DF. O apresentador aparece em câmera no canto inferior direito.
* **[00:30 – 01:30]**: Animação gráfica do fluxo de dados: Entrada de Áudio MP3 ➔ Transcrição Local Whisper ➔ Triagem XGBoost/SHAP ➔ Busca Vetorial FAISS (PCDTs) ➔ Orquestração LLM Multi-Provedor ➔ Prontuário SOAP com Rastreio de Violência Doméstica.
* **[01:30 – 02:30]**: Exibição do diagrama de blocos destacando a camada de redundância `chamar_llm()` com alternância entre Gemini (Google) e OpenAI.

#### Locução e Fala do Apresentador

> **[00:00 – 00:30] Apresentador:**
> "Sejam bem-vindos à apresentação do **Guardiã AI — Inteligência Artificial para a Saúde e Segurança da Mulher**, projeto desenvolvido para o Tech Challenge da Quinta Fase da Pós-Tech em IA para Devs da FIAP. A nossa equipe é formada por servidores da Secretaria de Segurança Pública do Distrito Federal. Desenvolvemos esta solução com um duplo objetivo: reduzir a carga burocrática dos profissionais de saúde na redação de prontuários e instituir um mecanismo ativo e automatizado de triagem contra a violência doméstica durante o atendimento clínico."

> **[00:30 – 01:30] Apresentador:**
> "A aplicação recebe o áudio bruto de uma consulta médica simulada e executa um pipeline sequencial de ponta a ponta. O áudio é transcrito localmente via modelo Whisper, enquanto o risco clínico do paciente é estimado por um algoritmo XGBoost munido de explicabilidade matemática via SHAP. Simultaneamente, a inteligência da aplicação realiza buscas no repositório oficial de Protocolos Clínicos e Diretrizes Terapêuticas (PCDT) do Ministério da Saúde vetorizados no FAISS, culminando na emissão de um relatório médico traduzido e de um Prontuário estruturado no padrão SOAP."

> **[01:30 – 02:30] Apresentador:**
> "Para garantir resiliência operacional absoluta em cenários de alta demanda no serviço público, o núcleo generativo adota uma arquitetura multi-provedor através da função `chamar_llm()`. O sistema utiliza o modelo Gemini, da Google, como provedor principal. Caso ocorra esgotamento de cota de requisições (HTTP 429), indisponibilidade do modelo (HTTP 404) ou falha na chave de API, a aplicação realiza um *fallback* automático e transparente para a plataforma da OpenAI, assegurando continuidade sem perda do progresso do atendimento."

---

### Bloco 2: Aquisição, Conversão e Fragmentação de PCDTs — `PCDTs.ipynb` (02:30 – 05:00)

* **Duração**: 2 minutos e 30 segundos
* **Objetivo**: Demonstrar o funcionamento do web crawler do Ministério da Saúde, a conversão paralela dos PDFs em Markdown e a divisão semântica por títulos.

#### Orientação de Cena e Recursos Visuais
* **[02:30 – 03:30]**: Gravação de tela do notebook `PCDTs.ipynb` mostrando a execução do crawler em BeautifulSoup, acessando o portal `gov.br/saude/pt-br/assuntos/pcdt/` de "A" a "Z" e baixando os PDFs.
* **[03:30 – 04:15]**: Terminal do Google Colab exibindo o log de inicialização do `ProcessPoolExecutor` utilizando múltiplos núcleos de CPU (`multiprocessing.cpu_count()`) e a conversão de 177 PDFs com `pymupdf4llm`.
* **[04:15 – 05:00]**: Exibição da estrutura dos arquivos `.md` gerados na pasta `PCDTs_Markdown_Processados`, destacando os cabeçalhos `#`, `##`, `###` preservados pelo `MarkdownHeaderTextSplitter`.

#### Locução e Fala do Apresentador

> **[02:30 – 03:30] Apresentador:**
> "A base de conhecimento do Guardiã AI é fundamentada nas diretrizes oficiais do Sistema Único de Saúde. No notebook independente `PCDTs.ipynb`, construímos um crawler automatizado que navega pelo portal do Ministério da Saúde. O código percorre iterativamente o índice alfabético de 'A' a 'Z', extrai as URLs limpas e decodifica o cabeçalho `Content-Disposition` enviado pelo servidor para capturar os nomes exatos das patologias. Ao todo, o script baixa 177 arquivos PDF oficiais, gerando o pacote consolidado `PCDTs_Completos.zip`."

> **[03:30 – 04:15] Apresentador:**
> "Converter quase duas centenas de documentos PDF extensos e complexos exige alta eficiência computacional. Para viabilizar esse processamento sem estouro de memória, o script implementa paralelismo distribuído através das bibliotecas `pymupdf4llm` e `ProcessPoolExecutor`. A conversão detecta automaticamente a quantidade de núcleos da CPU do ambiente e distribui a extração do texto, preservando tabelas e formatação estruturada de diretrizes complexas como as de Acidente Vascular Cerebral, Oncologia e Doenças Raras."

> **[04:15 – 05:00] Apresentador:**
> "Após a extração textual, os dados passam pela fragmentação semântica através do `MarkdownHeaderTextSplitter`. O divisor utiliza a hierarquia natural de títulos das diretrizes médicas — cabeçalhos de nível 1, 2 e 3 — como pontos de corte, injetando metadados como a patologia de origem e o nome do arquivo original em cada *chunk*. Todo o acervo processado é compactado no arquivo `PCDTs_Markdown.zip`, pronto para ser consumido pelo motor de indexação."

---

### Bloco 3: Indexação Vetorial e RAG Incremental Local/Offline — `etapa3_1_local.py` (05:00 – 08:00)

* **Duração**: 3 minutos
* **Objetivo**: Explicar o pipeline de vetorização offline, o modelo de embeddings multilíngue, a detecção de alterações por SHA-256 e a gestão de checkpoints.

#### Orientação de Cena e Recursos Visuais
* **[05:00 – 06:00]**: Visualização do código `etapa3_1_local.py` no VS Code. Animação destacando a classe `E5Embeddings` e os prefixos obrigatórios `passage:` e `query:`.
* **[06:00 – 07:00]**: Diagrama do mecanismo incremental: Cálculo de hash SHA-256 por arquivo ➔ Comparação com `manifest.json` ➔ Fingerprint por chunk ➔ Exclusão automatizada de vetores obsoletos no FAISS.
* **[07:00 – 08:00]**: Exibição dos arquivos de controle `checkpoint.json`, `embedding_config.json` e o log de sincronização com o diretório espelhado no Google Drive Desktop (`/MyDrive/PCDT_FAISS_E5`).

#### Locução e Fala do Apresentador

> **[05:00 – 06:00] Apresentador:**
> "Para eliminar custos de API e evitar o reprocessamento de embeddings na nuvem a cada execução do Colab, desenvolvemos o script `etapa3_1_local.py`. Este módulo roda localmente no ambiente do desenvolvedor e gera o banco vetorial FAISS utilizando o modelo de embeddings multilíngue `intfloat/multilingual-e5-base`, da Hugging Face. O modelo gera vetores densos de 768 dimensões com suporte a 94 idiomas. Através de um adaptador customizado do LangChain, o sistema insere o prefixo `passage:` para os textos dos PCDTs e `query:` para as buscas de consulta."

> **[06:00 – 07:00] Apresentador:**
> "O grande avanço arquitetural deste componente é a sua operação incremental resiliente. O script calcula o hash SHA-256 de cada documento Markdown e compara com o arquivo `manifest.json` anterior. Arquivos inalterados são ignorados instantaneamente. Se um protocolo for modificado pelo Ministério da Saúde, o algoritmo identifica os *chunks* antigos via *fingerprint* individual, deleta especificamente esses vetores no FAISS e insere apenas os fragmentos atualizados, prevenindo consultas clínicas baseadas em diretrizes obsoletas."

> **[07:00 – 08:00] Apresentador:**
> "O processamento de vetorização é estruturado em lotes com salvamento assíncrono em `checkpoint.json` e gravação imediata do arquivo `index.faiss`. Em caso de interrupção abrupta do sistema, a vetorização pode ser retomada do exato ponto em que parou. Ao final, a função de sincronização espelha os artefatos diretamente na pasta do Google Drive Desktop, disponibilizando uma base com 28.514 vetores prontos para carregamento instantâneo no Colab."

---

### Bloco 4: Notebook Principal — Triagem, Machine Learning e Voz (08:00 – 11:00)

* **Duração**: 3 minutos
* **Objetivo**: Demonstrar a execução das células de inicialização, a síntese de dados fictícios com Faker, o treinamento do XGBoost/SHAP e a análise vocal via Librosa.

#### Orientação de Cena e Recursos Visuais
* **[08:00 – 09:00]**: Gravação de tela do notebook `GUARDIA_IA_FASE_5.ipynb` (Células 1 a 4). Destaque para os comandos `pip install` silenciosos, configuração das chaves em `userdata` e geração do dataset com 5.000 registros.
* **[09:00 – 10:00]**: Gráficos das matrizes de confusão comparando o XGBoost e a Regressão Logística. Destaque para o valor de Recall (1.0000 no XGBoost vs 0.8398 na Regressão Logística) e a saída do texto explicativo SHAP.
* **[10:00 – 11:00]**: Demonstração do Motor de Análise Vocal com a biblioteca Librosa (Célula 8), exibindo a extração do gráfico de ondas, taxa de hesitação (silêncios > 30 dB) e desvio padrão de pitch (F0).

#### Locução e Fala do Apresentador

> **[08:00 – 09:00] Apresentador:**
> "Adentrando o notebook principal `GUARDIA_IA_FASE_5.ipynb`, as células iniciais tratam da instalação modular de dependências, autenticação multi-provedor e montagem do Google Drive. Na Célula 4, a aplicação constrói um dataset sintético de triagem clínica com 5.000 registros via biblioteca `Faker`. Os dados simulam sinais vitais, idade, comorbidades e taxas de hesitação vocal. O rótulo de `urgencia_critica` é atribuído por uma regra clínica determinística baseada na saturação de oxigênio abaixo de 93% ou combinação de frequência cardíaca elevada com hesitação."

> **[09:00 – 10:00] Apresentador:**
> "Na etapa de modelagem preditiva, treinamos um classificador XGBoost com ajuste de desbalanceamento de classes via `scale_pos_weight`. Para fornecer transparência médica, a função `analisar_risco_shap()` utiliza o `TreeExplainer` da biblioteca SHAP para gerar justificativas textuais que explicam ao profissional quais variáveis vitais mais elevaram o risco do paciente. Na avaliação sobre o conjunto de teste de 1.000 casos, o XGBoost priorizou a eliminação de Falsos Negativos, alcançando Recall de 1,0000 frente ao *baseline* de 0,8398 da Regressão Logística."

> **[10:00 – 11:00] Apresentador:**
> "Na Célula 8, opera o Motor de Análise Vocal alimentado pela biblioteca `Librosa`. A função `analisar_tom_e_hesitacao()` processa o sinal digital do áudio do paciente e extrai biomarcadores vocais: mede a taxa de hesitação — considerando intervalos de silêncio superiores a 30 dB — e calcula a variação da frequência fundamental de pitch. A combinação dessas métricas permite categorizar a resposta do paciente em tom 'Estável', 'Alta Hesitação' (silêncios acima de 25%) ou 'Tom Instável/Emocional' (desvio de pitch acima de 50 Hz)."

---

### Bloco 5: Transcrição, RAG Avançado e Módulo de Violência Doméstica (11:00 – 14:00)

* **Duração**: 3 minutos
* **Objetivo**: Apresentar a ingestão do MP3, transcrição Whisper em inglês, RAG multiconsulta com MMR e o módulo de segurança em 4 camadas para violência doméstica.

#### Orientação de Cena e Recursos Visuais
* **[11:00 – 11:45]**: Animação do upload do arquivo de áudio de teste (`RES0016.mp3`) e a execução do modelo Whisper `large` local, gerando a transcrição fiel com o *prompt* de contexto médico.
* **[11:45 – 12:45]**: Fluxo visual da chamada única de preparo em JSON: Tradução para PT-BR ➔ Geração da consulta principal e secundárias ➔ Busca no FAISS com Maximal Marginal Relevance (MMR) e teto de 14.000 caracteres de contexto.
* **[12:45 – 14:00]**: Destaque para as 4 camadas do Módulo de Violência Doméstica, exibindo a varredura das expressões regulares (Regex PT/EN), a injeção do RAG dirigido e a rede de segurança pós-geração `garantir_orientacao_violencia()`.

#### Locução e Fala do Apresentador

> **[11:00 – 11:45] Apresentador:**
> "A pipeline de atendimento inicia com o upload do arquivo MP3 da consulta. O áudio é transcrito localmente pelo modelo `Whisper large` com parâmetro `language='en'` e um *prompt* inicial de contexto clínico. Manter a transcrição original em inglês durante a ingestão é uma estratégia deliberada de otimização de tokens: a estrutura de *tokenization* das LLMs consome até 60% menos tokens em texto em inglês, reduzindo drasticamente o custo e a latência da requisição inicial."

> **[11:45 – 12:45] Apresentador:**
> "Para evitar o envio da transcrição bruta ao banco de dados — o que estouraria o teto de 512 tokens do modelo de embeddings E5 —, o Guardiã AI executa uma chamada de preparo via LLM que retorna um JSON estruturado. A requisição traduz o relato para o português do Brasil, formula uma 'consulta clínica principal' curta e mapeia até 4 hipóteses diagnósticas secundárias. O retriever realiza buscas combinadas no FAISS aplicando a técnica de *Maximal Marginal Relevance* (MMR) e deduplicação, selecionando os trechos de PCDTs mais diversos e pertinentes sem ultrapassar 14.000 caracteres de contexto."

> **[12:45 – 14:00] Apresentador:**
> "O diferencial de proteção à mulher do Guardiã AI é o seu Módulo de Violência Doméstica, construído sobre uma arquitetura de segurança em 4 camadas:
> 1. **Pré-análise por LLM**: Identifica se o médico questionou sobre o tema e classifica o nível de indício em 'relato', 'suspeita' ou 'nenhum'.
> 2. **Varredura por Expressões Regulares (Regex)**: Executa uma busca por termos-gatilho de agressão e medo em português e inglês de forma independente do LLM e de cotas de API.
> 3. **RAG Dirigido**: Ao detectar qualquer alerta, injeta automaticamente uma busca vetorial focada em 'atenção integral a pessoas em situação de violência'.
> 4. **Rede de Segurança Pós-Geração**: A função `garantir_orientacao_violencia()` insere obrigatoriamente as orientações para oferta de encaminhamento imediato ao CRAM, Casa da Mulher Brasileira, DEAM e notificação compulsória SINAN, em estrito cumprimento às Leis nº 10.778/2003 e nº 13.931/2019."

---

### Bloco 6: Relatório SOAP, Validação, Ética e Encerramento (14:00 – 15:00)

* **Duração**: 1 minuto
* **Objetivo**: Demonstrar o relatório impresso na tela e salvo em `.md`, ressaltar as regras de preservação e encerrar a apresentação acadêmica.

#### Orientação de Cena e Recursos Visuais
* **[14:00 – 14:35]**: Rolagem da tela exibindo o relatório gerado em `/content/relatorio_guardia_ai.md`. Destaque para os dados do paciente, transcrição exata da Portaria do PCDT recuperado, checkboxes (`☒`/`☐`) de violência doméstica e a estrutura SOAP completa.
* **[14:35 – 15:00]**: Retorno do apresentador em tela cheia, com infográfico dos pilares de Ética, LGPD e Supervisão Humana, seguido da tela final de créditos e contatos.

#### Locução e Fala do Apresentador

> **[14:00 – 14:35] Apresentador:**
> "Ao término da execução, o relatório final é apresentado na tela do console e salvo no arquivo `relatorio_guardia_ai.md`. A saída traz os Dados do Paciente, a Análise do Relato, as Diretrizes do PCDT com a citação exata da Portaria do Ministério da Saúde recuperada dos metadados — prevenindo alucinações normativas —, a seção de Avaliação de Violência Doméstica com caixas de seleção interativas e o Prontuário médico estruturado no padrão SOAP: Subjetivo, Objetivo, Avaliação e Plano."

> **[14:35 – 15:00] Apresentador:**
> "Reforçamos que o Guardiã AI é um protótipo de pesquisa acadêmica desenvolvido para o Tech Challenge da FIAP e atua estritamente como ferramenta de apoio à decisão, mantendo o profissional de saúde no centro da conduta clínica, em total conformidade com a LGPD e os preceitos éticos da inteligência artificial médica. Agradecemos à banca examinadora pela atenção!"

---

## 4. Matriz Resumo de Cenas, Tempos e Componentes Técnicos

| Bloco | Intervalo | Foco Técnico | Recurso Visual | Componente / Código |
| :--- | :--- | :--- | :--- | :--- |
| **1** | 00:00 – 02:30 | Visão Geral & Arquitetura Multi-Provedor | Diagrama de fluxo e mapa da função `chamar_llm()` | `GUARDIA_IA_FASE_5.ipynb` (Células 1 e 2) |
| **2** | 02:30 – 05:00 | Web Crawler, Paralelismo & Chunking Semântico | Gravação do processamento de 177 PDFs com CPU multi-core | `PCDTs.ipynb` (`pymupdf4llm` e `ProcessPoolExecutor`) |
| **3** | 05:00 – 08:00 | Vector Store Offline, Hashes SHA-256 e Checkpoints | Diagrama de comparação de manifestos e arquivos `.json` | `etapa3_1_local.py` (`Multilingual-E5-base` e `FAISS`) |
| **4** | 08:00 – 11:00 | Dataset Sintético, XGBoost/SHAP & Librosa | Gráficos SHAP, matrizes de confusão e ondas de áudio | `GUARDIA_IA_FASE_5.ipynb` (Células 4 a 8) |
| **5** | 11:00 – 14:00 | Transcrição Whisper, RAG MMR e Violência Doméstica | Animação do JSON de preparo e filtros Regex PT/EN | `GUARDIA_IA_FASE_5.ipynb` (Células 9 a 14) |
| **6** | 14:00 – 15:00 | Prontuário SOAP, Regras Antialucinação & LGPD | Exibição do relatório Markdown e tela final de encerramento | `/content/relatorio_guardia_ai.md` |
