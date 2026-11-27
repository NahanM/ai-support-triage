from typing import Protocol

from app.models.chamado import ChamadoEntrada
from app.models.classificacao import Categoria, ClassificacaoIA, Tipo


class ClassificacaoIndisponivel(Exception):
    """A IA não conseguiu classificar: fora do ar, demorou demais ou respondeu fora do formato."""


class Classificador(Protocol):
    """Contrato de qualquer classificador, seja fake, Gemini ou Ollama."""

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA: ...


class ClassificadorFake:
    """Devolve sempre a mesma classificação. Usado nos testes."""

    def __init__(self, classificacao: ClassificacaoIA | None = None):
        self.classificacao = classificacao or ClassificacaoIA(
            categoria=Categoria.DIARIO_CLASSE,
            tipo=Tipo.BUG,
            sistema_parado=False,
            resumo="Classificacao fixa para testes.",
        )

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA:
        return self.classificacao
    
    
class ClassificadorDesligado:
    """Usado quando não há chave de IA: sempre indisponível, e a triagem segue sem classificação."""

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA:
        raise ClassificacaoIndisponivel("nenhuma chave de IA configurada")