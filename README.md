# 👩‍⚕️👨‍💻 Guardiã AI - Inteligência Artificial para Saúde e Segurança da Mulher

[![FIAP Postech em IA para Devs](https://img.shields.io/badge/FIAP-Postech%20IA%20para%20Devs-blue?style=for-the-badge)](https://www.fiap.com.br/)
[![Fase 5 - Tech Challenge](https://img.shields.io/badge/Fase_5-Tech_Challenge-purple?style=for-the-badge)](https://github.com/marceloklotz/fiap-quinta-fase/)

Este repositório contém o código-fonte e as especificações técnicas desenvolvidos no âmbito do desafio (Tech Challenge) apresentado durante a Quinta Fase da Pós Tech (8IADT), da Faculdade de Informática e Administração Paulista (FIAP), conforme requisitos contidos no PDF disponível no presente repositório. O desafio propõe a criação do **Guardiã AI - Inteligência Artificial para Saúde e Segurança da Mulher**, uma aplicação capaz de receber informações de um atendimento e utilizar Inteligência Artificial para auxiliar na análise inicial do caso, auxiliando às equipes profissionais atuantes em questões voltadas à saúde da mulher e à segurança da mulher. 

## 🎙️ Solução de Análise de Áudio para Atendimento Clínico
Uma solução *end-to-end* projetada para apoiar consultas de ginecologia ou obstetrícia a partir do áudio capturado na relação médico-paciente.
* **Processamento Digital de Sinais (DSP):** Extração local de biomarcadores acústicos (tom de voz e taxas de hesitação) sem dependência de nuvem, preservando a latência e a privacidade de dados sensíveis da paciente.
* **Transcrição Automatizada (ASR):** Emprego do modelo **OpenAI Whisper** de forma nativa para transcrição de áudio clínico de forma robusta e resistente a ruídos hospitalares de fundo.
* **Estruturação Cognitiva (LLM):** Integração via sintaxe declarativa **LCEL (LangChain Expression Language)** com Engenharia de Prompt Defensiva para traduzir, contextualizar termos técnicos e gerar automaticamente um prontuário médico estruturado no padrão internacional **SOAP** (Subjetivo, Objetivo, Avaliação e Plano).

## ⚠️ Aviso de Uso Acadêmico e Isenção de Responsabilidade

> **IMPORTANTE:** Os componentes deste repositório foram desenvolvidos exclusivamente para fins educacionais, científicos e de demonstração de viabilidade tecnológica. 
> * **Não substituem validações médicas oficiais.**
> * **Não estão aptos para embasar decisões clínicas em tempo real, realizar diagnósticos ou apoiar triagens hospitalares.**
> * Toda e qualquer interpretação ou uso derivado deste código deve ficar estritamente sob a supervisão de profissionais de saúde competentes.

## 👥 Integrantes do grupo
Os membros do grupo são compostos pelos seguintes servidores da **Secretaria de Segurança Pública do Distrito Federal (SSP/DF)**:

- Alexandre Natã Vicente (**rm370024**) (ale.n.vicente@gmail.com)
- Antônio Cláudio Almeida (**rm370052**) (antonioalmeida@gmail.com)
- Cyd Ferreira Rodrigues (**rm370004**) (cydnelson@gmail.com)
- David Catherink (**rm369997**) (d.catherinck@gmail.com)
- Marcelo Macedo Klotz (**rm370010**) (marceloklotz@gmail.com) 

<picture>
  <img src="https://img.shields.io/badge/-ebebeb?style=for-the-badge&logoColor=black" width="100%" height="10px" alt="Integrantes do Grupo">
</picture>

# 🛠️ Detalhamento e Aplicação Prática das Tecnologias

Para garantir o funcionamento integrado e robusto do ecossistema multimodal, cada tecnologia e biblioteca desempenha um papel estratégico bem definido no código:

* **`openai-whisper`**
  * **Onde é utilizada:** Na camada inicial de processamento e acessibilidade de áudio.
  * **Aplicação prática:** Atua localmente como o motor de Reconhecimento Automático de Fala (ASR). Ela recebe os arquivos de áudio contendo as gravações das consultas e realiza a decodificação da voz em texto transcrito nativo em português.
* **`librosa`**
  * **Onde é utilizada:** Na extração local de biomarcadores acústicos (DSP - Processamento Digital de Sinais).
  * **Aplicação prática:** Analisa matematicamente o áudio bruto sem dependência de APIs em nuvem. É usada para calcular a frequência fundamental (Pitch) — fornecendo insumos sobre o tom emocional —, detectar zonas de silêncio e metrificar pausas ou taxas de hesitação na fala da paciente.
* **`langchain` / `langchain-core` / `langchain-openai`**
  * **Onde é utilizada:** Na orquestração lógica de inteligência generativa.
  * **Aplicação prática:** Constrói a esteira cognitiva utilizando a sintaxe declarativa **LCEL (LangChain Expression Language)**. Conecta as saídas textuais do Whisper aos modelos LLM, aplicando Engenharia de Prompt Defensiva para assegurar que o texto médico cru seja estruturado estritamente sob as regras e divisões internacionais do prontuário **SOAP**.
* **`deep-translator`**
  * **Onde é utilizada:** Na compatibilização e tradução linguística automatizada.
  * **Aplicação prática:** Utilizada para automatizar a tradução rápida de termos biomédicos específicos durante as etapas intermediárias de processamento, evitando que barreiras linguísticas comprometam a assertividade das instruções fornecidas à inteligência artificial.
* **`transformers` & `tiktoken`**
  * **Onde é utilizada:** No monitoramento de fluxos textuais e governança de custos.
  * **Aplicação prática:** O `tiktoken` faz a contagem preditiva exata e o corte preventivo dos tokens gerados pela transcrição do áudio clínico antes de enviá-los ao LLM, garantindo que o texto não ultrapasse a janela máxima de contexto da API e prevenindo erros de estouro de memória.

* **`numpy` & `pandas`**
  * **Onde são utilizadas:** Na manipulação matemática, estruturação de dados e geração de métricas.
  * **Aplicação prática:** O `numpy` manipula de forma veloz matrizes e tensores numéricos (sejam os pixels das imagens no OpenCV ou os arrays de ondas sonoras no Librosa). O `pandas` organiza as tabelas com o histórico das predições, taxas de acerto e logs, gerando as tabelas e dados estatísticos consolidados no relatório técnico.
 
# 📊 Dataset Utilizado

**Áudio — Audio Recording Whisper:** [Disponível via Kaggle](https://www.kaggle.com/datasets/najamahmed97/audio-recording-whisper). 

Conjunto de dados composto por diálogos médicos e simulações de consultas clínicas padronizadas pelo formato SOAP.

# 📁 Fluxo (pipeline)

```text

│   ├── Entrada dos dados → análise por Machine Learning → consulta de informações → interpretação utilizando LLM → apresentação dos resultados para um profissional.

```

## 📒 Relatório técnico

O Relatório Técnico, disponível pelo link abaixo, detalha todo o passo-a-passo para a construção dos módulos:


<p align="center">
  <picture><img src="https://github.com/marceloklotz/fiap-quarta-fase/blob/main/assets/relatorio.png" alt="Realatório"></picture>
</p>

## 📽️ Vídeo explicativo

O vídeo explicativo sobre a metologia, resultados e código-fonte utilizado foi disponbilizado a partir do link abaixo:

<p align="center">
<picture>
  <img src="#" width="100%" alt="Integrantes do Grupo">
</picture>
</p>
<p align="center"> Acesso ao vídeo: -------------  </p>
