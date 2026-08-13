import pytest
from pydantic import ValidationError

from app.models.chamado import ChamadoEntrada


def test_chamado_valido_e_aceito():
    chamado = ChamadoEntrada(
        titulo="Diário não salva presença",
        descricao="Depois da atualização nenhum professor consegue salvar presença.",
        usuarios_afetados=15,
        possui_workaround=False,
    )
    assert chamado.usuarios_afetados == 15


def test_titulo_apenas_espacos_e_rejeitado():
    with pytest.raises(ValidationError):
        ChamadoEntrada(
            titulo="        ",
            descricao="Depois da atualização nenhum professor consegue salvar presença.",
            usuarios_afetados=15,
            possui_workaround=False,
        )

def test_descricao_apenas_espacos_e_rejeitada():
    with pytest.raises(ValidationError):
        ChamadoEntrada(
            titulo="teste",
            descricao="          " ,
            usuarios_afetados=15,
            possui_workaround=False,
        )

def test_usuarios_afetados_zero_e_rejeitado():
    with pytest.raises(ValidationError):
        ChamadoEntrada(
            titulo="teste",
            descricao="Depois da atualização nenhum professor consegue salvar presença.",
            usuarios_afetados=0,
            possui_workaround=False,
        )

def test_descricao_ausente_e_rejeitada():
    with pytest.raises(ValidationError):
        ChamadoEntrada(
            titulo="Diário não salva presença",
            usuarios_afetados=15,
            possui_workaround=False,
        )