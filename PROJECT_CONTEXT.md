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
| Linguagem | Python | 3.14.2 |
| Validação | Pydantic | 2.13.4 |
| API | FastAPI + uvicorn | — |
| Testes | pytest | 9.1.1 |
| Orquestração | n8n | pendente |
| IA | Gemini (API gratuita) ou Ollama local | pendente |
| Infra | Docker Compose | pendente |
| Persistência | SQLite | pendente |

Ambiente: Windows, PowerShell, venv em `.venv/` na raiz.

---

## Arquitetura

```
n8n (orquestrador)
 ├─→ POST /chamados/validar     → descarta chamados malformados
 ├─→ IA (classificação)          → interpreta o texto
 ├─→ POST /chamados/prioridade   → score e rótulo
 └─→ IF: CRITICA → escalar | resto → registrar
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
    ├── app/
    │   ├── main.py             (FastAPI + rotas)
    │   ├── models/chamado.py   (contratos Pydantic)
    │   ├── rules/prioridade.py (funções puras de score)
    │   └── services/validacao.py
    └── tests/
        ├── test_api.py
        ├── test_chamado.py
        ├── test_prioridade.py
        └── test_validacao.py
```

Critério de pasta: **precisa de rede, banco, arquivo ou relógio → `services/`.
Só depende dos argumentos → `rules/`.**

---

## Decisões tomadas

**Nomenclatura em português** em todo o código e API.

**n8n chama a IA diretamente** (não o Python). Mantém o n8n como orquestrador
real em vez de wrapper fino. Workflows exportados para `n8n/workflows/*.json`.

**Python é dono do SQLite.** O n8n não escreve no banco — chama um endpoint.
Evita lock entre containers e mantém o schema versionado no código.

**Campos estruturados do usuário não são reinterpretados pela IA.**
`usuarios_afetados` vem do formulário; a IA não opina sobre ele. Cada ponto do
score é rastreável até sua origem.

**`/chamados/validar` recebe `dict` cru, não `ChamadoEntrada`.** Se fosse
tipado, o FastAPI validaria antes e devolveria 422 em inglês — a função nunca
rodaria e o endpoint não teria propósito. A rota existe para o n8n descartar
chamados ruins antes de gastar tempo de IA.

**`/chamados/prioridade` recebe `ChamadoEntrada` tipado.** Pressupõe chamado já
validado; quem chama fora de ordem recebe 422. Sem duplicar validação.

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
| Sistema crítico | +3 | tabela categoria→crítico (pendente) |
| Sistema totalmente parado | +2 | classificação da IA (pendente) |

Faixas: `>= 7` CRITICA · `>= 4` MEDIA · abaixo BAIXA. Máximo 10.

Com só dois fatores implementados, o score máximo atual é 5 — CRITICA ainda
não é alcançável na prática.

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

26 testes, todos passando.

```powershell
cd C:\Users\Public\n8n\ai-support-triage
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

Núcleo Python determinístico completo e testado. Nenhuma integração externa
ainda. Repositório em `github.com/<usuario>/ai-support-triage`, branch `main`.

---

## Próximo passo

Criar o `Classificador` com a implementação fake — o contrato que permite
montar o fluxo completo de triagem sem IA rodando.

Depois: `ClassificadorGemini` usando a API gratuita do Google AI Studio.

---

## Restrição de hardware

Notebook de desenvolvimento tem **4 GB de RAM**. Não roda Ollama junto com
Docker e n8n. Acesso a uma máquina melhor (do curso) é incerto.

Consequências:

- Etapas 1 a 4 e o classificador: feitas no notebook, Python nativo, sem Docker
- Etapas 5 a 12 (Docker, n8n, Ollama): dependem de outra máquina
- Gemini via API gratuita é o caminho provável para a IA
- Quando houver acesso à máquina boa: **gravar fixtures** com respostas reais
  do modelo em `tests/fixtures/` e **gravar vídeo** do `docker compose up` para
  o README

---

## Pendências

- `StarletteDeprecationWarning` sobre `httpx` → `httpx2`. Revisar ao fixar
  versões no `requirements.txt`
- Fixar versões com `pip freeze` quando o projeto estabilizar
- Handler global de exceções no FastAPI, com logging
- Pydantic aceita `"15"` (string) onde espera int e converte. Avaliar modo
  estrito quando o n8n estiver mandando dados reais
- Definir a taxonomia fechada de categorias (a IA precisa de lista fechada)
- Tabela categoria → sistema crítico
- Configuração de fim de linha (CRLF/LF) ao entrar no Docker
- README com a documentação do fallback de IA