from fastapi import Depends, FastAPI

from app.models.chamado import (
    ChamadoEntrada,
    PedidoPrioridade,
    ResultadoPrioridade,
    ResultadoTriagem,
    ResultadoValidacao,
)
from app.models.classificacao import ClassificacaoIA
from app.rules.prioridade import calcular_score, classificar_prioridade
from app.services.classificador import Classificador, ClassificadorFake
from app.services.triagem import classificar_sem_derrubar, triar
from app.services.validacao import validar_chamado

app = FastAPI(
    title="AI Support Triage",
    description="API de validação e priorização determinística de chamados.",
)


def obter_classificador() -> Classificador:
    """Qual classificador a API usa. Na Fase 3 passa a ser o Gemini."""
    return ClassificadorFake()


@app.post("/chamados/validar", response_model=ResultadoValidacao)
def endpoint_validar_chamado(dados: dict) -> ResultadoValidacao:
    """Valida a estrutura de um chamado antes do processamento."""
    return validar_chamado(dados)


@app.post("/chamados/classificar", response_model=ClassificacaoIA | None)
def endpoint_classificar_chamado(
    chamado: ChamadoEntrada,
    classificador: Classificador = Depends(obter_classificador),
) -> ClassificacaoIA | None:
    """Pede a classificação à IA. Devolve null se ela estiver indisponível."""
    return classificar_sem_derrubar(chamado, classificador)


@app.post("/chamados/prioridade", response_model=ResultadoPrioridade)
def endpoint_calcular_prioridade(pedido: PedidoPrioridade) -> ResultadoPrioridade:
    """Calcula score e prioridade a partir do chamado e da classificação."""
    score = calcular_score(pedido.chamado, pedido.classificacao)
    return ResultadoPrioridade(
        score=score,
        prioridade=classificar_prioridade(score),
    )


@app.post("/chamados/triar", response_model=ResultadoTriagem)
def endpoint_triar_chamado(
    dados: dict,
    classificador: Classificador = Depends(obter_classificador),
) -> ResultadoTriagem:
    """Atalho: valida, classifica e pontua numa chamada só."""
    return triar(dados, classificador)