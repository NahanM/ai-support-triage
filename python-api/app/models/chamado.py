from pydantic import BaseModel, ConfigDict, Field

from app.models.classificacao import ClassificacaoIA


class ChamadoEntrada(BaseModel):
    """Dados brutos de um chamado, como chegam do n8n."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    titulo: str = Field(min_length=5, max_length=120)
    descricao: str = Field(min_length=20, max_length=5000)
    usuarios_afetados: int = Field(ge=1)
    possui_workaround: bool


class ResultadoValidacao(BaseModel):
    """Resposta da validação, no formato que o n8n consome."""

    valido: bool
    erros: list[str] = []
    chamado: ChamadoEntrada | None = None


class ResultadoPrioridade(BaseModel):
    """Resposta da priorização, no formato que o n8n usa para rotear."""

    score: int
    prioridade: str 
    
    
class PedidoPrioridade(BaseModel):
    """O que o n8n manda para a /chamados/prioridade: o chamado e a leitura da IA."""

    model_config = ConfigDict(extra="forbid")

    chamado: ChamadoEntrada
    classificacao: ClassificacaoIA | None = None


class ResultadoTriagem(BaseModel):
    """Resposta completa da triagem, do chamado cru até a prioridade."""

    valido: bool
    erros: list[str] = []
    classificacao: ClassificacaoIA | None = None
    score: int | None = None
    prioridade: str | None = None