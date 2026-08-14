from fastapi import FastAPI

from app.models.chamado import ChamadoEntrada, ResultadoPrioridade, ResultadoValidacao
from app.rules.prioridade import calcular_score, classificar_prioridade
from app.services.validacao import validar_chamado

app = FastAPI(
    title="AI Support Triage",
    description="API de validação e priorização determinística de chamados.",
)


@app.post("/chamados/validar", response_model=ResultadoValidacao)
def endpoint_validar_chamado(dados: dict) -> ResultadoValidacao:
    """Valida a estrutura de um chamado antes do processamento."""
    return validar_chamado(dados)


@app.post("/chamados/prioridade", response_model=ResultadoPrioridade)
def endpoint_calcular_prioridade(chamado: ChamadoEntrada) -> ResultadoPrioridade:
    """Calcula score e prioridade de um chamado já validado."""
    score = calcular_score(chamado)
    return ResultadoPrioridade(
        score=score,
        prioridade=classificar_prioridade(score),
    )