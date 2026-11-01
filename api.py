
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

ARQUIVO_MODELO = (
    BASE_DIR / "modelos" / "modelo_atraso.joblib"
)

app = FastAPI(
    title="PulseOps AI",
    description=(
        "API de previsão de risco de atraso em entregas "
        "utilizando dados sintéticos."
    ),
    version="1.0.0",
)


# ==========================================
# 2. CARREGAMENTO DO MODELO
# ==========================================

if not ARQUIVO_MODELO.exists():
    raise FileNotFoundError(
        "Modelo não encontrado. "
        "Execute treinar_modelo.py primeiro."
    )

modelo = joblib.load(ARQUIVO_MODELO)


# ==========================================
# 3. VALIDAÇÃO DOS DADOS DE ENTRADA
# ==========================================

class Pedido(BaseModel):

    distancia_km: int = Field(ge=0, le=10000)

    volume_transportadora: int = Field(
        ge=0,
        le=1000000
    )

    periodo_pico: int = Field(ge=0, le=1)

    prazo_previsto_dias: int = Field(
        ge=1,
        le=365
    )

    regiao: str = Field(
        min_length=1,
        max_length=30
    )

    transportadora: str = Field(
        min_length=1,
        max_length=50
    )


# ==========================================
# 4. ROTA INICIAL
# ==========================================

@app.get("/")
def inicio():

    return {
        "projeto": "PulseOps AI",
        "status": "API funcionando",
        "versao": "1.0.0",
    }


# ==========================================
# 5. VERIFICAÇÃO DA API
# ==========================================

@app.get("/saude")
def verificar_saude():

    return {
        "status": "operacional",
        "modelo_carregado": modelo is not None,
    }


# ==========================================
# 6. PREVISÃO DE ATRASO
# ==========================================

@app.post("/prever")
def prever_atraso(pedido: Pedido):

    try:

        dados = pd.DataFrame([
            pedido.model_dump()
        ])

        probabilidade = float(
            modelo.predict_proba(dados)[0][1]
        )

        previsao = int(
            probabilidade >= 0.5
        )

        if probabilidade < 0.30:
            risco = "Baixo"

        elif probabilidade < 0.70:
            risco = "Moderado"

        else:
            risco = "Alto"

        return {
            "pedido": pedido.model_dump(),

            "previsao": (
                "Atrasado"
                if previsao == 1
                else "No prazo"
            ),

            "probabilidade_atraso": round(
                probabilidade * 100,
                2
            ),

            "nivel_risco": risco,

            "aviso": (
                "Previsão baseada em dados sintéticos."
            ),
        }

    except Exception as erro:

        raise HTTPException(
            status_code=500,
            detail="Erro ao realizar a previsão."
        ) from erro
