"""Mostra uma triagem passo a passo. Rodar de dentro de python-api: python rastrear.py"""

from app.rules.prioridade import calcular_score, classificar_prioridade
from app.services.classificador import ClassificadorFake
from app.services.triagem import classificar_sem_derrubar
from app.services.validacao import validar_chamado

CHAMADO = {
    "titulo": "Diário não salva presença",
    "descricao": "Depois da atualização nenhum professor consegue salvar presença.",
    "usuarios_afetados": 15,
    "possui_workaround": False,
}


def main():
    print("1. Chamado recebido:")
    print(f"   {CHAMADO}")

    validacao = validar_chamado(CHAMADO)
    print(f"\n2. Validação: {'ok' if validacao.valido else 'inválido'}")
    if not validacao.valido:
        for erro in validacao.erros:
            print(f"   - {erro}")
        return

    classificacao = classificar_sem_derrubar(validacao.chamado, ClassificadorFake())
    print(f"\n3. Classificação da IA: {classificacao}")

    score = calcular_score(validacao.chamado, classificacao)
    print(f"\n4. Score: {score}")
    print(f"5. Prioridade: {classificar_prioridade(score)}")


if __name__ == "__main__":
    main()