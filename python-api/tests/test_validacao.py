from app.services.validacao import validar_chamado

CHAMADO_OK = {
    "titulo": "Diário não salva presença",
    "descricao": "Depois da atualização nenhum professor consegue salvar presença.",
    "usuarios_afetados": 15,
    "possui_workaround": False,
}


def test_chamado_valido_retorna_valido_true():
    resultado = validar_chamado(CHAMADO_OK)

    assert resultado.valido is True
    assert resultado.erros == []
    assert resultado.chamado.usuarios_afetados == 15


def test_chamado_invalido_nao_levanta_excecao():
    resultado = validar_chamado({"titulo": "abc"})

    assert resultado.valido is False
    assert resultado.chamado is None


def test_erros_de_varios_campos_vem_juntos():
    resultado = validar_chamado({"titulo": "abc"})

    assert len(resultado.erros) == 4

def test_chamado_valido_devolve_dados_limpos():
    resultado = validar_chamado({
        "titulo": "   Diário não salva presença   ",
        "descricao": "Depois da atualização nenhum professor consegue salvar presença.",
        "usuarios_afetados": 15,
        "possui_workaround": False,
    })

    assert resultado.chamado.titulo == "Diário não salva presença"

    