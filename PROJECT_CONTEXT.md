# PROJECT_CONTEXT

Arquivo de memória do projeto. Serve para retomar o desenvolvimento em outra
conversa sem precisar reexplicar o que já foi feito.

---

## Objetivo do projeto

Sistema de triagem de chamados de suporte. Recebe chamados em linguagem
natural, valida, classifica com IA e calcula prioridade.

**Tese central:** a prioridade NÃO é decidida pelo modelo de IA. Ela é
calculada por regras determinísticas explícitas em Python. A IA só interpreta
linguagem natural.

---

## Stack

| Camada | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.14.7 |
| Validação | Pydantic | 2.14.4 |
| API | FastAPI + uvicorn | 0.165.0 + 0.54.0 |
| Testes | pytest | 9.2.0 |
| Orquestração | n8n | pendente |
| IA | Gemini (API gratuita) | pendente |
| Infra | Docker Compose | pendente |
| Persistência | SQLite | pendente |

Ambiente: Windows, PowerShell, venv em `.venv/` na raiz.

---

## Arquitetura

```
n8n (orquestrador)
 ├─→ recebe o chamado (webhook ou formulário)
 ├─→ POST /chamados/validar      → inválido: responde ao usuário e para
 ├─→ POST /chamados/classificar  → o Python chama o Gemini; se falhar, segue sem classificação
 ├─→ POST /chamados/prioridade   → recebe chamado + classificação, valida de novo e pontua
 ├─→ IF: CRITICA → escalar | resto → segue
 └─→ POST /chamados              → o Python grava no SQLite
```

Divisão de responsabilidades:

- **IA** → interpretação de linguagem natural
- **Python** → regras determinísticas e lógica de negócio
- **n8n** → orquestração e roteamento
- **Docker** → infraestrutura

---

## Estrutura relevante

```
ai-support-triage/
├── .gitignore
├── .venv/                      (ignorado pelo git)
└── python-api/
    ├── pytest.ini              (pythonpath = . , testpaths = tests)
    ├── requirements.txt
    ├── run.py                  (sobe o uvicorn)
    ├── rastrear.py             (mostra uma triagem passo a passo)
    ├── app/
    │   ├── main.py             (FastAPI + rotas)
    │   ├── models/
    │   │   ├── chamado.py      (contratos Pydantic)
    │   │   └── classificacao.py (Enums e ClassificacaoIA)
    │   ├── rules/prioridade.py (funções puras de score)
    │   └── services/
    │       ├── validacao.py
    │       ├── classificador.py (interface, Fake e ClassificacaoIndisponivel)
    │       └── triagem.py      (valida, classifica e pontua)
    └── tests/
        ├── test_api.py
        ├── test_chamado.py
        ├── test_classificacao.py
        ├── test_prioridade.py
        ├── test_triagem.py
        └── test_validacao.py
```

Critério de pasta: **precisa de rede, banco, arquivo ou relógio → `services/`.
Só depende dos argumentos → `rules/`.**

---

## Decisões tomadas

**Nomenclatura em português** em todo o código e API.

**O n8n orquestra etapa por etapa; o Python é quem fala com a IA.** (Substitui
"n8n chama a IA diretamente".) Cada etapa é uma rota separada, e o n8n decide o
caminho: chamado inválido para, IA fora do ar segue sem bônus, CRITICA escala.
A chave do Gemini, o tempo limite e a queda para o modo sem IA ficam no Python,
testáveis no pytest. A `/chamados/prioridade` recebe a classificação vinda do
n8n e valida de novo com `ClassificacaoIA`: o que passa pelo n8n não é confiável
por padrão. O `services/triagem.py` junta as etapas para os testes e para uma
rota `/chamados/triar` de atalho. Workflows exportados para `n8n/workflows/*.json`.

**Bônus de sistema crítico só vale para `bug` e `incidente`.** Dúvida ou
solicitação numa categoria crítica não é problema crítico ("esqueci minha senha"
caía em MEDIA). Limite conhecido: o `tipo` vem da IA; se ela classificar a senha
como `incidente`, o chamado sobe para MEDIA. O teste
`test_limite_conhecido_senha_classificada_como_incidente` documenta isso. A
defesa fica no prompt do Gemini.

**Python é dono do SQLite.** O n8n não escreve no banco — chama um endpoint.
Evita lock entre containers e mantém o schema versionado no código.

**Campos estruturados do usuário não são reinterpretados pela IA.**
`usuarios_afetados` vem do formulário; a IA não opina sobre ele. Cada ponto do
score é rastreável até sua origem.

**`/chamados/validar` recebe `dict` cru, não `ChamadoEntrada`.** Se fosse
tipado, o FastAPI validaria antes e devolveria 422 em inglês — a função nunca
rodaria e o endpoint não teria propósito. A rota existe para o n8n descartar
chamados ruins antes de gastar tempo de IA.

**`/chamados/prioridade` recebe `ChamadoEntrada` tipado.** Muda na Fase 2:
passa a receber chamado + classificação (opção C).

**Validação devolve todos os erros de uma vez**, não só o primeiro.

**`except Exception` genérico é proibido em `validar_chamado()`.** Bug interno
deve subir e quebrar alto, não virar "chamado inválido" e culpar o usuário.
Tratamento genérico vai num handler global do FastAPI, com log.

**Classificador atrás de uma interface** (`ClassificadorFake` / `Gemini` /
`Ollama`). Permite testes sem rede e troca de provedor por configuração.

---

## Regras de prioridade

| Fator | Pontos | Origem |
|---|---|---|
| 1 usuário | +1 | campo do chamado |
| 2 a 9 usuários | +2 | campo do chamado |
| 10+ usuários | +3 | campo do chamado |
| Sem workaround | +2 | campo do chamado |
| Sistema crítico (só bug ou incidente) | +3 | categoria e tipo da IA |
| Sistema totalmente parado | +2 | classificação da IA |

Faixas: `>= 7` CRITICA · `>= 4` MEDIA · abaixo BAIXA. Máximo 10.

---

## Features concluídas

**Etapas 1 e 2 — contrato e validação**
`ChamadoEntrada` (titulo 5-120, descricao 20-5000, usuarios_afetados >= 1,
possui_workaround obrigatório; `str_strip_whitespace`, `extra="forbid"`).
`validar_chamado()` converte `ValidationError` em `ResultadoValidacao`.

**Etapa 3 — regras de prioridade**
`pontuar_usuarios_afetados()`, `calcular_score()`, `classificar_prioridade()`.
Funções puras em `rules/`, sem I/O.

**Etapa 4 — API HTTP**
`POST /chamados/validar` e `POST /chamados/prioridade`. Documentação
automática em `/docs`.

---

## Testes existentes

50 testes, todos passando

```powershell
cd C:\Users\Natha\ai-support-triage-main
.venv\Scripts\Activate.ps1
cd python-api
python -m pytest -v
```

**Sempre rodar de `python-api`**, nunca da raiz nem de dentro de `app/`.
Fora dessa pasta o `pytest.ini` não é lido e o import de `app` falha.

Para subir o servidor: `python run.py` (o `run.py` existe porque
`python -m uvicorn` estava morrendo logo após iniciar no PowerShell).

---

## Estado atual

Núcleo determinístico, interface do classificador e ClassificadorFake prontos. Repositório em github.com/NahanM/ai-support-triage.

---

## Próximo passo

Fase 3: ClassificadorGemini

---

## Restrição de hardware

PC de desenvolvimento com **4 GB de RAM** (3,8 GB úteis). Docker roda via WSL2
limitado a 1,5 GB em `C:\Users\Natha\.wslconfig`.

Consequências:

- Ollama está fora: não cabe junto com Docker e n8n. A IA é o Gemini via API
- Cabem a API e o n8n nos contêineres, cada um com limite de memória no compose
- Fixtures com respostas reais do Gemini em `tests/fixtures/`
- Vídeo do `docker compose up` para o README

---

## Pendências

- Handler global de exceções no FastAPI, com logging
- Pydantic aceita `"15"` (string) onde espera int e converte. Avaliar modo
  estrito quando o n8n estiver mandando dados reais
- Configuração de fim de linha (CRLF/LF) ao entrar no Docker
- README com a documentação do fallback de IA
- IA fora do ar faz o score errar pra baixo (crítico vira MEDIA). Na Fase 6, o n8n manda chamados com `classificacao` vazia para revisão humana