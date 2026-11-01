
from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_rota_inicial():
    resposta = client.get("/")
    assert resposta.status_code == 200


def test_saude_api():
    resposta = client.get("/saude")
    assert resposta.status_code == 200


def test_previsao_atraso():
    dados = {
        "distancia_km": 1500,
        "volume_transportadora": 300,
        "periodo_pico": 1,
        "prazo_previsto_dias": 5,
        "regiao": "Sudeste",
        "transportadora": "TransLog A"
    }

    resposta = client.post("/prever", json=dados)

    assert resposta.status_code == 200

    resultado = resposta.json()

    assert "previsao" in resultado
    assert "probabilidade_atraso" in resultado
    assert "nivel_risco" in resultado
    assert "aviso" in resultado

    assert resultado["previsao"] in ["Atrasado", "No prazo"]
    assert 0 <= resultado["probabilidade_atraso"] <= 100
