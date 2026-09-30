# 👩‍⚕️👨‍💻 Guardiã AI - Inteligência Artificial para Saúde e Segurança da Mulher: Relatórios Gerados

[![FIAP Postech em IA para Devs](https://img.shields.io/badge/FIAP-Postech%20IA%20para%20Devs-blue?style=for-the-badge)](https://www.fiap.com.br/)
[![Fase 5 - Tech Challenge](https://img.shields.io/badge/Fase_5-Tech_Challenge-purple?style=for-the-badge)](https://github.com/marceloklotz/fiap-quinta-fase/)
[![Relatórios Gerados](https://img.shields.io/badge/Relatórios_Gerados-green?style=for-the-badge)](#)

## 🧬 Dataset Sintético de Triagem (Guardiã AI)

Essa pasta contém um **exemplos** de Relatórios gerados pelo Notebook principal, os quais são armazenados em cache após sua execução. 

O relatório é gerado a partir da função `gerar_prontuario_soap_en`, que é o cérebro clínico do sistema. Ela utiliza o LLM configurado na Etapa 4 (**Gemini** como principal e **OpenAI** como subsidiário, via o despachante resiliente `chamar_llm`) para consolidar todas as informações coletadas e gerar um prontuário médico estruturado no padrão **SOAP** (Subjetivo, Objetivo, Avaliação e Plano).

A arquitetura desta etapa foi desenhada com forte ênfase em **segurança clínica, objetividade e controle de custos**, utilizando as seguintes estratégias:

### ⚙️ Configuração Restrita da LLM (Teto Rígido)
* **`temperature=0.2`:** Mantém o modelo altamente determinístico e focado. Na área médica, queremos precisão e não "criatividade", evitando que a IA invente informações.
* **`max_tokens=2000`:** Define um limite para o tamanho da resposta (trava de custo). O valor é maior que o anterior (600) porque modelos de raciocínio (Gemini *thinking* e OpenAI GPT-5/6) consomem tokens "pensando" e ficariam sem espaço para responder.

### 🛡️ Engenharia de Prompt Defensiva
O *Prompt* (instrução dada à IA) foi escrito em inglês para otimizar o uso de tokens e possui **restrições explícitas (Constraints)**:
* Obriga o uso de *bullet points* (tópicos curtos), proibindo parágrafos longos.
* Instrução antialucinação: Se não houver dados para uma seção, a IA deve escrever apenas *"Not reported"* (Não relatado), impedindo que ela preencha lacunas com invenções.
* Exige alinhamento estrito com os dados fornecidos e com os protocolos clínicos.

### 📋 Integração de Múltiplos Contextos e Estrutura SOAP
A cadeia de execução (`prompt | llm`) cruza quatro fontes de dados distintas:
1. **Dados do Paciente:** Histórico prévio.
2. **Protocolo PCDT:** Diretrizes clínicas oficiais que devem ser seguidas para diagnóstico e conduta.
3. **Transcrição:** O relato em texto gerado pelo Whisper.
4. **Análise Vocal:** Os insights acústicos de hesitação e estresse da Etapa 2.

A IA organiza tudo isso na clássica estrutura médica **SOAP**:
* **S (Subjective):** Sintomas relatados, incluindo os biomarcadores de voz (ex: paciente estava hesitante ao relatar a dor).
* **O (Objective):** Dados mensuráveis, sinais vitais ou exames (se citados).
* **A (Assessment):** Hipótese diagnóstica baseada nos sintomas e no protocolo PCDT.
* **P (Plan):** Plano de ação (medicamentos, exames, retorno) guiado rigorosamente pelo PCDT.

**Saída:** A função retorna o prontuário final em formato Markdown, pronto para ser lido pelo profissional de saúde de forma rápida e clara.

## ⚠️ Aviso de Uso Acadêmico e Isenção de Responsabilidade

> **IMPORTANTE:** Os componentes deste repositório foram desenvolvidos exclusivamente para fins educacionais, científicos e de demonstração de viabilidade tecnológica. 
> * **Não substituem validações médicas oficiais.**
> * **Não estão aptos para embasar decisões clínicas em tempo real, realizar diagnósticos ou apoiar triagens hospitalares.**
> * Toda e qualquer interpretação ou uso derivado deste código deve ficar estritamente sob a supervisão de profissionais de saúde competentes.
