from langchain_core.prompts import ChatPromptTemplate


REASONING_PROMPT_TEMPLATE = """
# CONTEXTO
Você é um motor de análise linguística. Sua tarefa é analisar a mensagem do usuário e raciocinar sobre a intenção e as entidades. 
A data de hoje é {today}. Seja objetivo.

# TAREFA
Analise a mensagem e forneça uma cadeia de pensamento sobre:
1. Qual é a ação principal que o usuário quer executar (agendar, consultar, atualizar, conversar)?
2. Quais são as peças de informação (entidades) fornecidas? (ex: tarefa="reunião", data="amanhã")
3. A intenção principal é clara ou é genuinamente impossível de determinar? (Falta de detalhes como 'horário' NÃO é uma ambiguidade de intenção).

# MENSAGEM DO USUÁRIO
{user_message}

# SEU RACIOCÍNIO:
"""
REASONING_PROMPT = ChatPromptTemplate.from_template(REASONING_PROMPT_TEMPLATE)


FORMATTING_PROMPT_TEMPLATE = """
# CONTEXTO
Você é um motor de extração de dados que segue um processo rigoroso de duas etapas.
ETAPA 1: Você recebe um raciocínio inicial sobre a mensagem de um usuário.
ETAPA 2: Você DEVE revisar esse raciocínio contra as REGRAS DE DECISÃO abaixo e, em seguida, preencher o formulário JSON final.

# REGRAS DE DECISÃO CRÍTICAS
1.  **REGRA DA AMBIGUIDADE DE INTENÇÃO:** Se a mensagem do usuário NÃO contém um verbo de ação claro (como 'marcar', 'o que tem', 'qual é', 'atualize'), ela é inerentemente ambígua.
    - EXEMPLO: "Relatório de amanhã". O raciocínio pode sugerir uma consulta, mas a frase não tem verbo. **REVISE E CONCLUA:** A intenção é ambígua. Defina 'is_ambiguous' como 'true'.
    - EXEMPLO: "lembrete de sexta". Lembrete do que? Não está explícito. **REVISE E CONCLUA:** A intenção é ambígua. Defina 'is_ambiguous' como 'true'.

2.  **REGRA DA TAREFA AUSENTE:** Se a intenção é clara (ex: 'agendar', 'marcar como feito'), mas o objeto da ação está faltando, a solicitação é ambígua.
    - EXEMPLO: "Agendar para o dia 20". Agendar o quê? **REVISE E CONCLUA:** A intenção é ambígua. Defina 'is_ambiguous' como 'true'.

3.  **REGRA DA CLAREZA:** Se um verbo de ação claro E um objeto de tarefa estão presentes, a solicitação NÃO é ambígua, mesmo que faltem detalhes secundários (como hora/local).
    - EXEMPLO: "marcar reunião para amanhã". Tem verbo ('marcar') e objeto ('reunião'). **REVISE E CONCLUA:** A intenção NÃO é ambígua.

# PROCESSO
1.  Leia o RACIOCÍNIO DO ANALISTA.
2.  Leia a MENSAGEM ORIGINAL DO USUÁRIO.
3.  Aplique as REGRAS DE DECISÃO CRÍTICAS para corrigir o raciocínio, se necessário.
4.  Preencha o JSON abaixo com base na sua conclusão final e revisada.

# RACIOCÍNIO DO ANALISTA
{reasoning}

# MENSAGEM ORIGINAL DO USUÁRIO
{user_message}

# INSTRUÇÕES DE FORMATAÇÃO
A data de hoje é {today}. Siga estritamente as instruções de formato JSON fornecidas em {format_instructions}. Sua resposta DEVE ser apenas o objeto JSON.
"""
FORMATTING_PROMPT = ChatPromptTemplate.from_template(FORMATTING_PROMPT_TEMPLATE)
