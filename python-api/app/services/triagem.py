import logging

from app.models.chamado import ChamadoEntrada, ResultadoTriagem
from app.models.classificacao import ClassificacaoIA
from app.rules.prioridade import calcular_score, classificar_prioridade
from app.services.classificador import Classificador, ClassificacaoIndisponivel
from app.services.validacao import validar_chamado

logger = logging.getLogger(__name__)


def classificar_sem_derrubar(
    chamado: ChamadoEntrada,
    classificador: Classificador,
) -> ClassificacaoIA | None:
    """Pede a classificação à IA. Se ela estiver indisponível, segue sem."""
    try:
        return classificador.classificar(chamado)
    except ClassificacaoIndisponivel as erro:
        logger.warning("IA indisponível, triagem segue sem classificação: %s", erro)
        return None
    
    
def triar(dados: dict, classificador: Classificador) -> ResultadoTriagem:
    """Valida, classifica e pontua um chamado numa chamada só."""
    validacao = validar_chamado(dados)
    if not validacao.valido:
        return ResultadoTriagem(valido=False, erros=validacao.erros)

    chamado = validacao.chamado
    classificacao = classificar_sem_derrubar(chamado, classificador)
    score = calcular_score(chamado, classificacao)

    return ResultadoTriagem(
        valido=True,
        classificacao=classificacao,
        score=score,
        prioridade=classificar_prioridade(score),
    )