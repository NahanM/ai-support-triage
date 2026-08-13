from app.models.chamado import ChamadoEntrada

PONTOS_USUARIO_UNICO = 1
PONTOS_POUCOS_USUARIOS = 2
PONTOS_MUITOS_USUARIOS = 3
PONTOS_SEM_WORKAROUND = 2

LIMITE_POUCOS_USUARIOS = 10


def pontuar_usuarios_afetados(quantidade: int) -> int:
    """Converte a quantidade de usuários em pontos, em faixas exclusivas."""
    if quantidade == 1:
        return PONTOS_USUARIO_UNICO
    if quantidade < LIMITE_POUCOS_USUARIOS:
        return PONTOS_POUCOS_USUARIOS
    return PONTOS_MUITOS_USUARIOS


def calcular_score(chamado: ChamadoEntrada) -> int:
    """Soma os fatores de gravidade do chamado."""
    score = pontuar_usuarios_afetados(chamado.usuarios_afetados)

    if not chamado.possui_workaround:
        score += PONTOS_SEM_WORKAROUND

    return score