from pydantic import ValidationError

from app.models.chamado import ChamadoEntrada, ResultadoValidacao


def validar_chamado(dados: dict) -> ResultadoValidacao:
    try:
        # Tenta transformar o dicionário recebido num ChamadoEntrada válido
        chamado_validado = ChamadoEntrada.model_validate(dados)
        
        # Se chegou aqui, os dados são válidos
        return ResultadoValidacao(
            valido=True,
            erros=[],
            chamado=chamado_validado
        )
        
    except ValidationError as e:
        # O Pydantic lança essa exceção se os dados não baterem com o modelo
        erros_formatados = []
        
        # Itera sobre os erros para formatar de um jeito legível para o n8n
        for erro in e.errors():
            # 'loc' é o caminho do campo (ex: 'titulo' ou 'cliente.nome')
            campo = ".".join([str(loc) for loc in erro['loc']])
            mensagem = erro['msg']
            erros_formatados.append(f"Campo '{campo}': {mensagem}")
            
        return ResultadoValidacao(
            valido=False,
            erros=erros_formatados,
            chamado=None
        )