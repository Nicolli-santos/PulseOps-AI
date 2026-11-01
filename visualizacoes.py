
import pandas as pd
import plotly.express as px

# ============================================================
# PULSEOPS AI - VISUALIZACOES
# ============================================================

# 1. Carregar os dados
df = pd.read_csv("dados_pedidos_sinteticos.csv")

# 2. Contar pedidos no prazo e atrasados
contagem = (
    df["atrasado"]
    .value_counts()
    .reindex([0, 1], fill_value=0)
    .rename(index={
        0: "No prazo",
        1: "Atrasados"
    })
    .rename_axis("situacao")
    .reset_index(name="quantidade")
)

# 3. Criar o grafico
fig = px.bar(
    contagem,
    x="situacao",
    y="quantidade",
    color="situacao",
    text="quantidade",
    title="PulseOps AI - Pedidos no Prazo vs. Atrasados",
    labels={
        "situacao": "Situacao do pedido",
        "quantidade": "Quantidade de pedidos"
    }
)

# 4. Ajustar a apresentacao
fig.update_traces(textposition="outside")
fig.update_layout(
    showlegend=False,
    template="plotly_white",
    yaxis_title="Quantidade de pedidos",
    xaxis_title="Situacao do pedido"
)

# 5. Exibir o grafico no navegador
fig.show()



# ============================================================
# GRAFICO 2 - TAXA DE ATRASO POR REGIAO
# ============================================================

# 1. Calcular a taxa de atraso de cada regiao
por_regiao = (
    df.groupby("regiao")["atrasado"]
    .mean()
    .mul(100)
    .reset_index(name="taxa_atraso")
)

# 2. Ordenar as regioes da maior para a menor taxa
por_regiao = por_regiao.sort_values(
    "taxa_atraso",
    ascending=False
)

# 3. Criar o grafico
fig_regiao = px.bar(
    por_regiao,
    x="regiao",
    y="taxa_atraso",
    text=por_regiao["taxa_atraso"].round(2).astype(str) + "%",
    title="PulseOps AI - Taxa de Atraso por Regiao",
    labels={
        "regiao": "Regiao",
        "taxa_atraso": "Taxa de atraso (%)"
    }
)

# 4. Ajustar a apresentacao
fig_regiao.update_traces(textposition="outside")
fig_regiao.update_layout(
    template="plotly_white",
    yaxis_title="Taxa de atraso (%)",
    xaxis_title="Regiao",
    yaxis_range=[0, 50]
)

# 5. Exibir o grafico
fig_regiao.show()



# ============================================================
# GRAFICO 3 - TAXA DE ATRASO POR FAIXA DE DISTANCIA
# ============================================================

# 1. Criar faixas de distancia
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

# 2. Calcular a taxa de atraso em cada faixa
por_distancia = (
    df.groupby("faixa_distancia", observed=False)["atrasado"]
    .mean()
    .mul(100)
    .reset_index(name="taxa_atraso")
)

# 3. Criar o grafico
fig_distancia = px.bar(
    por_distancia,
    x="faixa_distancia",
    y="taxa_atraso",
    text=por_distancia["taxa_atraso"].round(2).astype(str) + "%",
    title="PulseOps AI - Taxa de Atraso por Distancia",
    labels={
        "faixa_distancia": "Faixa de distância",
        "taxa_atraso": "Taxa de atraso (%)",
    },
)

# 4. Ajustar a apresentacao
fig_distancia.update_traces(textposition="outside")
fig_distancia.update_layout(
    template="plotly_white",
    xaxis_title="Distância de entrega",
    yaxis_title="Taxa de atraso (%)",
    yaxis_range=[0, 55],
)

# 5. Exibir o grafico
fig_distancia.show()
