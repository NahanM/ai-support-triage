from pydantic import BaseModel, ConfigDict, Field


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