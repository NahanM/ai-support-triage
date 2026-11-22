import pytest

from app.models.chamado import ChamadoEntrada
from app.models.classificacao import Categoria, ClassificacaoIA, Tipo
from app.rules.prioridade import (
    calcular_score,
    classificar_prioridade,
    pontuar_usuarios_afetados,
)


def montar_chamado(usuarios_afetados: int, possui_workaround: bool) -> ChamadoEntrada:
    return ChamadoEntrada(
        titulo="Diário não salva presença",
        descricao="Depois da atualização nenhum professor consegue salvar presença.",
        usuarios_afetados=usuarios_afetados,
        possui_workaround=possui_workaround,
    )


def montar_classificacao(categoria: Categoria, sistema_parado: bool, tipo: Tipo = Tipo.BUG) -> ClassificacaoIA:
    return ClassificacaoIA(
        categoria=categoria,
        tipo=tipo,
        sistema_parado=sistema_parado,
        resumo="Resumo de teste para classificacao.",
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


@pytest.mark.parametrize(
    "score, prioridade_esperada",
    [
        (1, "BAIXA"),
        (3, "BAIXA"),
        (4, "MEDIA"),
        (6, "MEDIA"),
        (7, "CRITICA"),
        (10, "CRITICA"),
    ],
)
def test_faixas_de_prioridade(score, prioridade_esperada):
    assert classificar_prioridade(score) == prioridade_esperada


def test_categoria_critica_soma_tres_pontos():
    chamado = montar_chamado(1, True)

    sem_ia = calcular_score(chamado)
    com_ia = calcular_score(chamado, montar_classificacao(Categoria.DIARIO_CLASSE, False))

    assert com_ia - sem_ia == 3


def test_categoria_nao_critica_nao_soma():
    chamado = montar_chamado(1, True)

    sem_ia = calcular_score(chamado)
    com_ia = calcular_score(chamado, montar_classificacao(Categoria.RELATORIOS, False))

    assert com_ia == sem_ia


def test_score_maximo_atinge_dez():
    chamado = montar_chamado(500, False)
    classificacao = montar_classificacao(Categoria.INFRAESTRUTURA, True)

    assert calcular_score(chamado, classificacao) == 10
    assert classificar_prioridade(10) == "CRITICA"


def test_sem_classificacao_usa_apenas_fatores_do_chamado():
    chamado = montar_chamado(500, False)

    assert calcular_score(chamado) == 5
    
    
def test_duvida_em_categoria_critica_nao_soma():
    chamado = montar_chamado(1, True)

    sem_ia = calcular_score(chamado)
    com_ia = calcular_score(
        chamado,
        montar_classificacao(Categoria.ACESSO, False, Tipo.DUVIDA),
    )

    assert com_ia == sem_ia


def test_incidente_de_acesso_soma_tres_pontos():
    chamado = montar_chamado(1, True)

    sem_ia = calcular_score(chamado)
    com_ia = calcular_score(
        chamado,
        montar_classificacao(Categoria.ACESSO, False, Tipo.INCIDENTE),
    )

    assert com_ia - sem_ia == 3


def test_esqueci_minha_senha_fica_baixa():
    # 1 usuario (+1), sem workaround (+2), duvida de acesso (sem bonus) = 3
    chamado = montar_chamado(1, False)
    classificacao = montar_classificacao(Categoria.ACESSO, False, Tipo.DUVIDA)

    score = calcular_score(chamado, classificacao)

    assert score == 3
    assert classificar_prioridade(score) == "BAIXA"


def test_limite_conhecido_senha_classificada_como_incidente():
    # Se a IA errar o tipo, a regra nao tem como saber.
    chamado = montar_chamado(1, False)
    classificacao = montar_classificacao(Categoria.ACESSO, False, Tipo.INCIDENTE)

    score = calcular_score(chamado, classificacao)

    assert score == 6
    assert classificar_prioridade(score) == "MEDIA"
    
    
@pytest.mark.parametrize("tipo", [Tipo.DUVIDA, Tipo.SOLICITACAO])
def test_duvida_e_solicitacao_nao_pontuam_em_notas(tipo):
    chamado = montar_chamado(1, True)

    sem_ia = calcular_score(chamado)
    com_ia = calcular_score(
        chamado,
        montar_classificacao(Categoria.NOTAS, False, tipo),
    )

    assert com_ia == sem_ia