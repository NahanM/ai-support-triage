from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CHAMADO_OK = {
    "titulo": "Diário não salva presença",
    "descricao": "Depois da atualização nenhum professor consegue salvar presença.",
    "usuarios_afetados": 15,
    "possui_workaround": False,
}


def test_validar_chamado_valido():
    resposta = client.post("/chamados/validar", json=CHAMADO_OK)

    assert resposta.status_code == 200
    assert resposta.json()["valido"] is True


def test_validar_chamado_invalido_devolve_200_com_erros():
    resposta = client.post("/chamados/validar", json={"titulo": "abc"})

    assert resposta.status_code == 200
    assert resposta.json()["valido"] is False
    assert len(resposta.json()["erros"]) == 4


def test_prioridade_de_chamado_valido():
    resposta = client.post("/chamados/prioridade", json=CHAMADO_OK)

    assert resposta.status_code == 200
    assert resposta.json() == {"score": 5, "prioridade": "MEDIA"}


def test_prioridade_rejeita_chamado_invalido_com_422():
    resposta = client.post("/chamados/prioridade", json={"titulo": "abc"})

    assert resposta.status_code == 422