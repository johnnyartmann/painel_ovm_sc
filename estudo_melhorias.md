# Estudo de Melhorias - Painel Observatório da Violência Contra a Mulher - SC

Este documento apresenta uma análise técnica do sistema atual e propõe melhorias divididas em quatro pilares: Arquitetura, UX/UI, Performance e Novas Funcionalidades.

## 1. Arquitetura e Qualidade de Código

### 1.1. Modularização e Reuso
**Diagnóstico:**
- Existe duplicação de lógica entre `tabs/analise_geral.py` e `tabs/analise_feminicidios.py`, especialmente nas funções de criação de tabelas (`criar_tabela_consolidada`, `criar_tabela_total_...`).
- Funções de plotagem em `plotting.py` possuem muitos blocos `if/else` para tratar diferentes tipos de gráficos, o que dificulta a manutenção e a adição de novos tipos.

**Proposta:**
- **Extrair Lógica Compartilhada:** Criar um módulo `services/analytics.py` para conter as funções de cálculos estatísticos e preparação de DataFrames para tabelas, removendo essa responsabilidade dos arquivos de visualização (tabs).
- **Refatorar Plotting:** Utilizar um padrão de *Strategy* ou dicionários de configuração para mapear tipos de gráficos (Barra, Linha, Pizza) para funções específicas ou configurações do Plotly, reduzindo a complexidade ciclomática.
- **Configuração Centralizada:** Criar um arquivo `config.py` ou `constants.py` para armazenar paletas de cores, configurações de layout padrão do Plotly e textos fixos. Hoje, cores hexadecimais (ex: `#8e24aa`) estão espalhadas pelo código.

### 1.2. Gerenciamento de Estado
**Diagnóstico:**
- O uso de `st.session_state` está disperso. A inicialização ocorre no `painel_observatorio.py`, mas a manipulação ocorre em vários lugares.

**Proposta:**
- **State Class:** Implementar uma classe `SessionState` para tipar e centralizar o acesso às variáveis de estado. Isso facilita o entendimento de quais dados persistem entre interações.

### 1.3. Testes Automatizados
**Diagnóstico:**
- Não foram identificados testes unitários ou de integração.

**Proposta:**
- **Adicionar Testes Unitários:** Focar na lógica de transformação de dados (ex: `preprocess_data.py` e funções de cálculo nas tabs). Ferramenta sugerida: `pytest`.
- **Testes de Interface (Opcional):** Utilizar o framework de testes nativo do Streamlit para garantir que os componentes renderizam sem erro.

## 2. Experiência do Usuário (UX) e Interface (UI)

### 2.1. Consistência Visual
**Diagnóstico:**
- O sistema já utiliza uma identidade visual (roxo), mas a consistência pode ser melhorada (ex: botões primários vs secundários com estilos inline CSS).

**Proposta:**
- **Theme Config:** Utilizar ao máximo o `theme.toml` do Streamlit para definir cores primárias e de fundo, reduzindo a necessidade de CSS injetado manualmente e garantindo compatibilidade com Dark Mode nativo.
- **Componentes Padronizados:** Criar wrappers para componentes comuns (ex: um componente `metric_card` reutilizável em vez de HTML string formatado em cada tab).

### 2.2. Interatividade
**Diagnóstico:**
- Os filtros estão na sidebar e recarregam a página inteira.

**Proposta:**
- **Formulários de Filtro:** Envolver os filtros da sidebar em um `st.form` com um botão "Aplicar Filtros". Isso evita recarregamentos desnecessários a cada clique em um checkbox, melhorando a percepção de performance.
- **Cross-filter (Avançado):** Utilizar eventos do Plotly (via `streamlit-plotly-events` ou callback nativo se disponível na versão mais recente) para que clicar em uma cidade no mapa filtre os outros gráficos automaticamente.

### 2.3. Acessibilidade
**Diagnóstico:**
- Gráficos dependem muito de cor para distinção.

**Proposta:**
- **Paletas Acessíveis:** Garantir que as paletas de cores sejam amigáveis para daltônicos (ex: usar texturas ou paletas `viridis`/`cividis` onde apropriado, embora o roxo seja a cor da causa, contrastes devem ser verificados).
- **Alt Text:** Adicionar descrições textuais para imagens e suporte melhorado a leitores de tela nos componentes HTML injetados.

## 3. Performance

### 3.1. Carregamento de Dados
**Diagnóstico:**
- `data_loader.py` carrega todos os parquets no início. Se a base crescer, isso aumentará o tempo de *startup*.

**Proposta:**
- **Lazy Loading:** Carregar DataFrames específicos apenas quando a aba correspondente for ativada (embora o Streamlit execute o script todo, pode-se usar lazy loading com o decorador de cache de forma mais granular).
- **Otimização de Parquet:** Verificar se os arquivos parquet estão particionados ou se colunas não utilizadas estão sendo carregadas.

### 3.2. Renderização de Gráficos
**Diagnóstico:**
- Gráficos Plotly podem ficar pesados com muitos pontos (ex: scatter plot com todos os casos).

**Proposta:**
- **Amostragem/Agregação:** Para visualizações de grandes volumes, usar *Datashader* ou agregar dados antes de enviar para o frontend, se o número de pontos for excessivo (milhares). Atualmente o volume parece gerenciavel, mas é um ponto de atenção para escalabilidade.

## 4. Novas Funcionalidades (Roadmap)

### 4.1. Análise Assistida por IA (Gemini)
**Oportunidade:**
- Integrar um botão "Gerar Relatório Inteligente" que pega o resumo dos dados filtrados (DataFrame consolidado) e envia para o modelo Gemini gerar um texto analítico automático, destacando tendências e anomalias que podem passar despercebidas no visual.

### 4.2. Sistema de Alertas
**Oportunidade:**
- Definir limiares (ex: aumento de 20% em casos em um município) e exibir alertas visuais destacados no painel.

### 4.3. Exportação de Relatórios PDF
**Oportunidade:**
- Melhorar a funcionalidade de impressão. Criar uma geração de PDF backend (usando `WeasyPrint` ou `FPDF`) que gera um relatório formatado e paginado profissionalmente, em vez de depender do `window.print()` do navegador que muitas vezes quebra layouts.

## Resumo das Prioridades

| Prioridade | Ação | Impacto | Esforço |
| :--- | :--- | :--- | :--- |
| **Alta** | Refatorar código duplicado e centralizar configurações (cores/estilos). | Manutenibilidade | Médio |
| **Alta** | Implementar `st.form` nos filtros da sidebar. | UX/Performance | Baixo |
| **Média** | Criar módulo de serviços para cálculos estatísticos. | Arquitetura | Médio |
| **Média** | Integração com IA para geração de insights textuais. | Inovação/Valor | Médio |
| **Baixa** | Geração de PDF no backend. | Funcionalidade | Alto |
