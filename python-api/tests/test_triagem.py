import pytest

from app.models.chamado import ChamadoEntrada
from app.models.classificacao import Categoria, ClassificacaoIA
from app.services.classificador import ClassificacaoIndisponivel, ClassificadorFake
from app.services.triagem import triar

CHAMADO_OK = {
    "titulo": "Diário não salva presença",
    "descricao": "Depois da atualização nenhum professor consegue salvar presença.",
    "usuarios_afetados": 15,
    "possui_workaround": False,
}


class ClassificadorQueFalha:
    """Simula a IA fora do ar."""

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA:
        raise ClassificacaoIndisponivel("simulando IA fora do ar")


class ClassificadorEspiao:
    """Conta quantas vezes a IA foi chamada."""

    def __init__(self):
        self.chamadas = 0

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA:
        self.chamadas += 1
        return ClassificadorFake().classificar(chamado)


class ClassificadorComBug:
    """Simula um erro de programação, não uma falha da IA."""

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA:
        raise KeyError("campo_que_nao_existe")


def test_chamado_invalido_nao_chama_a_ia():
    espiao = ClassificadorEspiao()

    resultado = triar({"titulo": "abc"}, espiao)

    assert resultado.valido is False
    assert len(resultado.erros) == 4
    assert resultado.score is None
    assert espiao.chamadas == 0


def test_ia_fora_do_ar_pontua_so_com_o_chamado():
    resultado = triar(CHAMADO_OK, ClassificadorQueFalha())

    # 15 usuarios (+3) e sem workaround (+2)
    assert resultado.valido is True
    assert resultado.classificacao is None
    assert resultado.score == 5
    assert resultado.prioridade == "MEDIA"


def test_chamado_completo():
    resultado = triar(CHAMADO_OK, ClassificadorFake())

    # 5 do chamado + 3 do diario_classe com tipo bug (o padrao do Fake)
    assert resultado.classificacao.categoria == Categoria.DIARIO_CLASSE
    assert resultado.score == 8
    assert resultado.prioridade == "CRITICA"


def test_bug_no_classificador_nao_e_engolido():
    with pytest.raises(KeyError):
        triar(CHAMADO_OK, ClassificadorComBug())