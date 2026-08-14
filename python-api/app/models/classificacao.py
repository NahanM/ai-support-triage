from enum import Enum

from pydantic import BaseModel, Field


class Categoria(str, Enum):
    DIARIO_CLASSE = "diario_classe"
    NOTAS = "notas"
    MATRICULA = "matricula"
    FINANCEIRO = "financeiro"
    RELATORIOS = "relatorios"
    ACESSO = "acesso"
    INFRAESTRUTURA = "infraestrutura"
    OUTROS = "outros"


class Tipo(str, Enum):
    BUG = "bug"
    DUVIDA = "duvida"
    SOLICITACAO = "solicitacao"
    INCIDENTE = "incidente"


class ClassificacaoIA(BaseModel):
    """O que a IA devolve. Validado antes de entrar no cálculo do score."""

    categoria: Categoria
    tipo: Tipo
    sistema_parado: bool
    resumo: str = Field(min_length=10, max_length=300)