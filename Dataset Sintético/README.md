# 👩‍⚕️👨‍💻 Guardiã AI - Inteligência Artificial para Saúde e Segurança da Mulher: Dataset Sintético

[![FIAP Postech em IA para Devs](https://img.shields.io/badge/FIAP-Postech%20IA%20para%20Devs-blue?style=for-the-badge)](https://www.fiap.com.br/)
[![Fase 5 - Tech Challenge](https://img.shields.io/badge/Fase_5-Tech_Challenge-purple?style=for-the-badge)](https://github.com/marceloklotz/fiap-quinta-fase/)
[![Dataset Sintético](https://img.shields.io/badge/Dataset_Sintético-green?style=for-the-badge)](#)

## 🧬 Dataset Sintético de Triagem (Guardiã AI)

Essa pasta contém um **exemplo** de dataset sintético gerado pelo Notebook principal, que é armazenado em cache após sua execução. O motor gera uma base de dados sintética com **5.000 registros** simulando o atendimento e triagem de pacientes. O objetivo é fornecer dados estruturados para testes de algoritmos de machine learning e análise preditiva.

<p align="center">
  <picture><img src="https://github.com/marceloklotz/fiap-quinta-fase/blob/main/assets/Guardiã_AI__Triagem_Preditiva.png" alt="Guardiã_AI__Triagem_Preditiva"></picture>
</p>

### ⚙️ Principais Funcionalidades e Premissas do Gerador:
* **Dados Demográficos e Identificação:** Utiliza a biblioteca `Faker` (configurada para o Brasil `pt_BR`) para gerar nomes limpos (sem títulos ou abreviaturas), datas de nascimento, CPFs e RGs.
* **Sinais Vitais Realistas:** Simula distribuições estatísticas (via distribuições normais acopladas a limites clínicos com `np.clip`) para pressão arterial, frequência cardíaca e respiratória, temperatura, saturação de oxigênio ($\text{SpO}_2$) e histórico de comorbidades.
* **Regra de Urgência Crítica:** Define um rótulo alvo (`urgencia_critica`) baseado em critérios clínicos simulados, como saturação baixa ou combinação de alta frequência cardíaca com taxa de hesitação elevada.
* **Rastreio de Violência Doméstica:** Modela probabilisticamente uma coluna de suspeita (`suspeita_violencia_domestica`) influenciada pelo gênero e por índices comportamentais de hesitação vocal, servindo estritamente como indicador de triagem e não diagnóstico fechado.
* **Exportação:** Salva o resultado final estruturado em um arquivo CSV (`dataset_guardia_ai_triagem.csv`) e imprime um resumo estatístico da distribuição por gênero e suspeitas mapeadas no console.

⚠️ **Nota**: Os resultados obtidos refletem o desempenho dos modelos sobre o dataset sintético construído para o projeto. Como a variável-alvo foi gerada por regras determinísticas, o desempenho observado, especialmente o resultado (perfeito) do XGBoost, **não deve ser interpretado como validação clínica ou como estimativa de desempenho em dados reais**.

## ⚠️ Aviso de Uso Acadêmico e Isenção de Responsabilidade

> **IMPORTANTE:** Os componentes deste repositório foram desenvolvidos exclusivamente para fins educacionais, científicos e de demonstração de viabilidade tecnológica. 
> * **Não substituem validações médicas oficiais.**
> * **Não estão aptos para embasar decisões clínicas em tempo real, realizar diagnósticos ou apoiar triagens hospitalares.**
> * Toda e qualquer interpretação ou uso derivado deste código deve ficar estritamente sob a supervisão de profissionais de saúde competentes.
