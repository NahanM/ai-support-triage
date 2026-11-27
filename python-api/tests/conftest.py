import pytest

from app.main import app, obter_classificador
from app.services.classificador import ClassificadorFake


@pytest.fixture(autouse=True)
def sem_ia_de_verdade():
    """Nenhum teste chama o Gemini de verdade: a internet fica de fora."""
    app.dependency_overrides[obter_classificador] = lambda: ClassificadorFake()
    yield
    app.dependency_overrides.clear()