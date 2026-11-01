
import pandas as pd

# ============================================================
# PULSEOPS AI
# Análise exploratória de dados sintéticos
# ============================================================

ARQUIVO = "dados_pedidos_sinteticos.csv"

# 1. Carregar os dados
df = pd.read_csv(ARQUIVO)

print("=" * 60)
print("PULSEOPS AI - ANÁLISE EXPLORATÓRIA")
print("=" * 60)

# 2. Dimensões da base
print("\n1. DIMENSÕES DA BASE")
print("-" * 40)
print(f"Linhas: {df.shape[0]}")
print(f"Colunas: {df.shape[1]}")

# 3. Tipos de dados
print("\n2. TIPOS DE DADOS")
print("-" * 40)
print(df.dtypes.to_string())

# 4. Valores ausentes
print("\n3. VALORES AUSENTES")
print("-" * 40)
print(df.isnull().sum().to_string())

# 5. Estatísticas das variáveis numéricas
print("\n4. ESTATÍSTICAS NUMÉRICAS")
print("-" * 40)
print(df.describe().round(2).to_string())

# 6. Distribuição dos atrasos
print("\n5. DISTRIBUIÇÃO DOS ATRASOS")
print("-" * 40)

contagem = df["atrasado"].value_counts().sort_index()
percentuais = (
    df["atrasado"]
    .value_counts(normalize=True)
    .sort_index()
    * 100
)

print(f"No prazo (0): {contagem.get(0, 0)}")
print(f"Atrasados (1): {contagem.get(1, 0)}")
print(f"Percentual de atrasos: {percentuais.get(1, 0):.2f}%")

# 7. Taxa de atraso por região
print("\n6. TAXA DE ATRASO POR REGIÃO")
print("-" * 40)

por_regiao = (
    df.groupby("regiao")["atrasado"]
    .agg(total_pedidos="count", total_atrasados="sum",
         taxa_atraso="mean")
)

por_regiao["taxa_atraso"] *= 100
print(por_regiao.round(2).sort_values(
    "taxa_atraso", ascending=False
).to_string())

# 8. Taxa de atraso por transportadora
print("\n7. TAXA DE ATRASO POR TRANSPORTADORA")
print("-" * 40)

por_transportadora = (
    df.groupby("transportadora")["atrasado"]
    .agg(total_pedidos="count", total_atrasados="sum",
         taxa_atraso="mean")
)

por_transportadora["taxa_atraso"] *= 100
print(por_transportadora.round(2).sort_values(
    "taxa_atraso", ascending=False
).to_string())

# 9. Taxa de atraso por faixa de distância
print("\n8. TAXA DE ATRASO POR DISTÂNCIA")
print("-" * 40)

df["faixa_distancia"] = pd.cut(
    df["distancia_km"],
    bins=[0, 500, 1000, 1500, 2000, float("inf")],
    labels=[
        "Até 499 km",
        "500 a 999 km",
        "1000 a 1499 km",
        "1500 a 1999 km",
        "2000 km ou mais",
    ],
    right=False,
)

por_distancia = (
    df.groupby("faixa_distancia", observed=False)["atrasado"]
    .agg(total_pedidos="count", total_atrasados="sum",
         taxa_atraso="mean")
)

por_distancia["taxa_atraso"] *= 100
print(por_distancia.round(2).to_string())

print("\nAnálise concluída.")
print("AVISO: os dados analisados são sintéticos.")

