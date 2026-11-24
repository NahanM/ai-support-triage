import pytest
from fastapi.testclient import TestClient

from app.main import app, obter_classificador
from app.models.chamado import ChamadoEntrada
from app.models.classificacao import ClassificacaoIA
from app.services.classificador import ClassificacaoIndisponivel

client = TestClient(app)

CHAMADO_OK = {
    "titulo": "Diário não salva presença",
    "descricao": "Depois da atualização nenhum professor consegue salvar presença.",
    "usuarios_afetados": 15,
    "possui_workaround": False,
}

CLASSIFICACAO_OK = {
    "categoria": "diario_classe",
    "tipo": "bug",
    "sistema_parado": False,
    "resumo": "Professores não conseguem salvar presença.",
}


class ClassificadorQueFalha:
    """Simula a IA fora do ar."""

    def classificar(self, chamado: ChamadoEntrada) -> ClassificacaoIA:
        raise ClassificacaoIndisponivel("simulando IA fora do ar")


@pytest.fixture
def ia_fora_do_ar():
    app.dependency_overrides[obter_classificador] = lambda: ClassificadorQueFalha()
    yield
    app.dependency_overrides.clear()


# /chamados/validar

def test_validar_chamado_valido():
    resposta = client.post("/chamados/validar", json=CHAMADO_OK)

    assert resposta.status_code == 200
    assert resposta.json()["valido"] is True


def test_validar_chamado_invalido_devolve_200_com_erros():
    resposta = client.post("/chamados/validar", json={"titulo": "abc"})

    assert resposta.status_code == 200
    assert resposta.json()["valido"] is False
    assert len(resposta.json()["erros"]) == 4


# /chamados/classificar

def test_classificar_devolve_classificacao():
    resposta = client.post("/chamados/classificar", json=CHAMADO_OK)

    assert resposta.status_code == 200
    assert resposta.json()["categoria"] == "diario_classe"


def test_classificar_com_ia_fora_do_ar_devolve_null(ia_fora_do_ar):
    resposta = client.post("/chamados/classificar", json=CHAMADO_OK)

    assert resposta.status_code == 200
    assert resposta.json() is None


# /chamados/prioridade

def test_prioridade_sem_classificacao():
    resposta = client.post("/chamados/prioridade", json={"chamado": CHAMADO_OK})

    assert resposta.status_code == 200
    assert resposta.json() == {"score": 5, "prioridade": "MEDIA"}


def test_prioridade_com_classificacao():
    pedido = {"chamado": CHAMADO_OK, "classificacao": CLASSIFICACAO_OK}

    resposta = client.post("/chamados/prioridade", json=pedido)

    assert resposta.json() == {"score": 8, "prioridade": "CRITICA"}


def test_prioridade_recusa_score_vindo_de_fora():
    pedido = {"chamado": CHAMADO_OK, "score": 10}

    resposta = client.post("/chamados/prioridade", json=pedido)

    assert resposta.status_code == 422


def test_prioridade_recusa_categoria_inventada():
    classificacao = {**CLASSIFICACAO_OK, "categoria": "urgentissimo"}
    pedido = {"chamado": CHAMADO_OK, "classificacao": classificacao}

    resposta = client.post("/chamados/prioridade", json=pedido)

    assert resposta.status_code == 422


def test_prioridade_rejeita_chamado_invalido_com_422():
    resposta = client.post("/chamados/prioridade", json={"chamado": {"titulo": "abc"}})

    assert resposta.status_code == 422


# /chamados/triar

def test_triar_chamado_completo():
    resposta = client.post("/chamados/triar", json=CHAMADO_OK)
    corpo = resposta.json()

    assert resposta.status_code == 200
    assert corpo["valido"] is True
    assert corpo["prioridade"] == "CRITICA"


def test_triar_chamado_invalido():
    resposta = client.post("/chamados/triar", json={"titulo": "abc"})

    assert resposta.status_code == 200
    assert resposta.json()["valido"] is False