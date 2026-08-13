import pytest

from app.models.chamado import ChamadoEntrada
from app.rules.prioridade import calcular_score, pontuar_usuarios_afetados


def montar_chamado(usuarios_afetados: int, possui_workaround: bool) -> ChamadoEntrada:
    return ChamadoEntrada(
        titulo="Diário não salva presença",
        descricao="Depois da atualização nenhum professor consegue salvar presença.",
        usuarios_afetados=usuarios_afetados,
        possui_workaround=possui_workaround,
    )


@pytest.mark.parametrize(
    "usuarios_afetados, pontos_esperados",
    [
        (1, 1),
        (2, 2),
        (9, 2),
        (10, 3),
        (500, 3),
    ],
)
def test_faixas_de_usuarios(usuarios_afetados, pontos_esperados):
    assert pontuar_usuarios_afetados(usuarios_afetados) == pontos_esperados


def test_sem_workaround_soma_dois_pontos():
    com = calcular_score(montar_chamado(1, True))
    sem = calcular_score(montar_chamado(1, False))

    assert sem - com == 2


def test_pior_caso_possivel():
    assert calcular_score(montar_chamado(500, False)) == 5