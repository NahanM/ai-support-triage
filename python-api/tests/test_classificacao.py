import pytest
from pydantic import ValidationError

from app.models.classificacao import Categoria, ClassificacaoIA, Tipo
from app.services.classificador import ClassificadorFake


def test_categoria_invalida_e_rejeitada():
    with pytest.raises(ValidationError):
        ClassificacaoIA(
            categoria="presenca_diario",
            tipo="bug",
            sistema_parado=False,
            resumo="Falha ao salvar presenca.",
        )


def test_classificacao_valida_e_aceita():
    classificacao = ClassificacaoIA(
        categoria="diario_classe",
        tipo="bug",
        sistema_parado=True,
        resumo="Falha ao salvar presenca apos atualizacao.",
    )

    assert classificacao.categoria == Categoria.DIARIO_CLASSE
    assert classificacao.sistema_parado is True


def test_fake_devolve_classificacao_padrao():
    fake = ClassificadorFake()

    resultado = fake.classificar(chamado=None)

    assert resultado.tipo == Tipo.BUG