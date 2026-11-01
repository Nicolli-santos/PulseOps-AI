
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

ARQUIVO_DADOS = BASE_DIR / "dados_pedidos_sinteticos.csv"

PASTA_MODELOS = BASE_DIR / "modelos"

ARQUIVO_MODELO = PASTA_MODELOS / "modelo_atraso.joblib"

COLUNAS_NUMERICAS = [
    "distancia_km",
    "volume_transportadora",
    "periodo_pico",
    "prazo_previsto_dias",
]

COLUNAS_CATEGORICAS = [
    "regiao",
    "transportadora",
]

COLUNAS_MODELO = COLUNAS_NUMERICAS + COLUNAS_CATEGORICAS

ALVO = "atrasado"


# ==========================================
# 2. CARREGAMENTO E VALIDAÇÃO DOS DADOS
# ==========================================

def carregar_dados():

    if not ARQUIVO_DADOS.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {ARQUIVO_DADOS}"
        )

    df = pd.read_csv(ARQUIVO_DADOS)

    colunas_necessarias = COLUNAS_MODELO + [ALVO]

    faltantes = [
        coluna
        for coluna in colunas_necessarias
        if coluna not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Colunas ausentes no arquivo: {faltantes}"
        )

    df = df[colunas_necessarias].copy()

    for coluna in COLUNAS_NUMERICAS + [ALVO]:
        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )

    df = df.dropna(subset=[ALVO])

    df = df[df[ALVO].isin([0, 1])]

    if df.empty:
        raise ValueError("Não existem registros válidos.")

    if df[ALVO].nunique() != 2:
        raise ValueError(
            "O conjunto precisa conter pedidos atrasados "
            "e pedidos não atrasados."
        )

    return df


# ==========================================
# 3. PREPARAÇÃO DOS DADOS
# ==========================================

def preparar_dados(df):

    X = df[COLUNAS_MODELO]

    y = df[ALVO].astype(int)

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    return X_treino, X_teste, y_treino, y_teste


# ==========================================
# 4. CONSTRUÇÃO DO MODELO
# ==========================================

def criar_modelo():

    processamento = ColumnTransformer(
        transformers=[
            (
                "numericas",
                Pipeline([
                    (
                        "imputacao",
                        SimpleImputer(strategy="median")
                    ),
                    (
                        "escala",
                        StandardScaler()
                    ),
                ]),
                COLUNAS_NUMERICAS,
            ),
            (
                "categoricas",
                Pipeline([
                    (
                        "imputacao",
                        SimpleImputer(strategy="most_frequent")
                    ),
                    (
                        "codificacao",
                        OneHotEncoder(handle_unknown="ignore")
                    ),
                ]),
                COLUNAS_CATEGORICAS,
            ),
        ]
    )

    modelo = Pipeline([
        ("processamento", processamento),
        (
            "classificador",
            LogisticRegression(
                max_iter=1000,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    ])

    return modelo


# ==========================================
# 5. TREINAMENTO E AVALIAÇÃO
# ==========================================

def avaliar_modelo(modelo, X_teste, y_teste):

    previsoes = modelo.predict(X_teste)

    probabilidades = modelo.predict_proba(X_teste)[:, 1]

    acuracia = accuracy_score(y_teste, previsoes)

    auc = roc_auc_score(y_teste, probabilidades)

    print("\n========== RESULTADOS DO MODELO ==========")

    print(f"\nAcurácia: {acuracia:.4f}")

    print(f"ROC-AUC: {auc:.4f}")

    print("\nRelatório de classificação:")

    print(
        classification_report(
            y_teste,
            previsoes,
            target_names=["No prazo", "Atrasado"],
            zero_division=0,
        )
    )

    print("Matriz de confusão:")

    print(
        confusion_matrix(
            y_teste,
            previsoes
        )
    )

    print("\n==========================================")

    return {
        "acuracia": acuracia,
        "roc_auc": auc,
    }


# ==========================================
# 6. SALVAMENTO DO MODELO
# ==========================================

def salvar_modelo(modelo):

    PASTA_MODELOS.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        modelo,
        ARQUIVO_MODELO
    )

    print("\nModelo salvo com sucesso!")

    print(f"Local: {ARQUIVO_MODELO}")


# ==========================================
# 7. EXECUÇÃO PRINCIPAL
# ==========================================

def main():

    print("Iniciando treinamento do PulseOps AI...")

    df = carregar_dados()

    print(f"\nRegistros válidos: {len(df)}")

    print("\nPreparando dados...")

    X_treino, X_teste, y_treino, y_teste = preparar_dados(df)

    print(f"Dados de treinamento: {len(X_treino)}")

    print(f"Dados de teste: {len(X_teste)}")

    print("\nConstruindo modelo...")

    modelo = criar_modelo()

    print("\nTreinando modelo...")

    modelo.fit(X_treino, y_treino)

    print("\nAvaliando modelo...")

    avaliar_modelo(
        modelo,
        X_teste,
        y_teste
    )

    salvar_modelo(modelo)

    print(
        "\nATENÇÃO: este projeto utiliza dados sintéticos. "
        "As métricas não representam resultados de operações reais."
    )

    print("\nTreinamento finalizado!")


if __name__ == "__main__":
    main()
