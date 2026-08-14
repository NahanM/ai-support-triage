from app.models.chamado import ChamadoEntrada
from app.models.classificacao import Categoria, ClassificacaoIA

PONTOS_USUARIO_UNICO = 1
PONTOS_POUCOS_USUARIOS = 2
PONTOS_MUITOS_USUARIOS = 3
PONTOS_SEM_WORKAROUND = 2

LIMITE_POUCOS_USUARIOS = 10
SCORE_MINIMO_CRITICA = 7
SCORE_MINIMO_MEDIA = 4

PONTOS_SISTEMA_CRITICO = 3
PONTOS_SISTEMA_PARADO = 2

CATEGORIAS_CRITICAS = {
    Categoria.DIARIO_CLASSE,
    Categoria.NOTAS,
    Categoria.MATRICULA,
    Categoria.ACESSO,
    Categoria.INFRAESTRUTURA,
}

def pontuar_usuarios_afetados(quantidade: int) -> int:
    """Converte a quantidade de usuários em pontos, em faixas exclusivas."""
    if quantidade == 1:
        return PONTOS_USUARIO_UNICO
    if quantidade < LIMITE_POUCOS_USUARIOS:
        return PONTOS_POUCOS_USUARIOS
    return PONTOS_MUITOS_USUARIOS

def calcular_score(
    chamado: ChamadoEntrada,
    classificacao: ClassificacaoIA | None = None,
) -> int:
    """Soma os fatores de gravidade. Funciona mesmo sem classificação da IA."""
    score = pontuar_usuarios_afetados(chamado.usuarios_afetados)

    if not chamado.possui_workaround:
        score += PONTOS_SEM_WORKAROUND

    if classificacao is None:
        return score

    if classificacao.categoria in CATEGORIAS_CRITICAS:
        score += PONTOS_SISTEMA_CRITICO

    if classificacao.sistema_parado:
        score += PONTOS_SISTEMA_PARADO

    return score

def classificar_prioridade(score: int) -> str:
    """Traduz o score numérico na prioridade que o n8n usa para rotear."""
    if score >= SCORE_MINIMO_CRITICA:
        return "CRITICA"
    if score >= SCORE_MINIMO_MEDIA:
        return "MEDIA"
    return "BAIXA"