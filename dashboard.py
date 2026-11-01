
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="PulseOps AI",
    page_icon="📦",
    layout="wide",
)


# ==========================================
# 1. CARREGAMENTO DOS DADOS
# ==========================================

@st.cache_data
def carregar_dados():
    return pd.read_csv("dados_pedidos_sinteticos.csv")


df = carregar_dados()


# ==========================================
# 2. IDENTIDADE DO DASHBOARD
# ==========================================

st.title("📦 PulseOps AI")
st.subheader("Painel inteligente de análise de entregas")

st.info(
    "Este painel utiliza dados sintéticos gerados para fins "
    "de estudo. Os resultados não representam dados reais "
    "de uma empresa."
)


# ==========================================
# 3. FILTRO POR REGIÃO
# ==========================================

st.subheader("Filtros")

regioes = ["Todas as regiões"] + sorted(
    df["regiao"].dropna().unique().tolist()
)

regiao_selecionada = st.selectbox(
    "Selecione uma região:",
    regioes,
)

if regiao_selecionada == "Todas as regiões":
    df_filtrado = df.copy()
else:
    df_filtrado = df[
        df["regiao"] == regiao_selecionada
    ].copy()


# ==========================================
# 4. INDICADORES
# ==========================================

total_pedidos = len(df_filtrado)

total_atrasados = int(
    df_filtrado["atrasado"].sum()
)

total_no_prazo = (
    total_pedidos - total_atrasados
)

taxa_atraso = (
    df_filtrado["atrasado"].mean() * 100
    if total_pedidos > 0
    else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total de pedidos",
    f"{total_pedidos:,}".replace(",", ".")
)

col2.metric(
    "Pedidos no prazo",
    f"{total_no_prazo:,}".replace(",", ".")
)

col3.metric(
    "Pedidos atrasados",
    f"{total_atrasados:,}".replace(",", ".")
)

col4.metric(
    "Taxa de atraso",
    f"{taxa_atraso:.2f}%"
)

st.divider()


# ==========================================
# 5. GRÁFICO DE SITUAÇÃO
# ==========================================

situacao = pd.DataFrame({
    "Situação": ["No prazo", "Atrasados"],
    "Quantidade": [
        total_no_prazo,
        total_atrasados,
    ],
})

fig_situacao = px.bar(
    situacao,
    x="Situação",
    y="Quantidade",
    color="Situação",
    text="Quantidade",
    title="Pedidos no prazo vs. atrasados",
)

fig_situacao.update_traces(
    textposition="outside"
)

fig_situacao.update_layout(
    template="plotly_white",
    showlegend=False,
    yaxis_title="Quantidade de pedidos",
    xaxis_title="",
)

st.subheader("Situação dos pedidos")

st.plotly_chart(
    fig_situacao,
    use_container_width=True
)


# ==========================================
# 6. TAXA DE ATRASO POR REGIÃO
# ==========================================

por_regiao = (
    df_filtrado.groupby("regiao")["atrasado"]
    .mean()
    .mul(100)
    .reset_index(name="taxa_atraso")
    .sort_values(
        "taxa_atraso",
        ascending=False
    )
)

fig_regiao = px.bar(
    por_regiao,
    x="regiao",
    y="taxa_atraso",
    text=(
        por_regiao["taxa_atraso"]
        .round(2)
        .astype(str) + "%"
    ),
    title="Comparação entre regiões",
    labels={
        "regiao": "Região",
        "taxa_atraso": "Taxa de atraso (%)",
    },
)

fig_regiao.update_traces(
    textposition="outside"
)

fig_regiao.update_layout(
    template="plotly_white",
    yaxis_range=[0, 50],
)

st.subheader("Taxa de atraso por região")

st.plotly_chart(
    fig_regiao,
    use_container_width=True
)


# ==========================================
# 7. TAXA DE ATRASO POR DISTÂNCIA
# ==========================================

df_filtrado["faixa_distancia"] = pd.cut(
    df_filtrado["distancia_km"],
    bins=[
        0, 500, 1000, 1500, 2000,
        float("inf"),
    ],
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
    df_filtrado.groupby(
        "faixa_distancia",
        observed=False
    )["atrasado"]
    .mean()
    .mul(100)
    .reset_index(name="taxa_atraso")
)

fig_distancia = px.bar(
    por_distancia,
    x="faixa_distancia",
    y="taxa_atraso",
    text=(
        por_distancia["taxa_atraso"]
        .round(2)
        .astype(str) + "%"
    ),
    title="Comparação entre faixas de distância",
    labels={
        "faixa_distancia": "Faixa de distância",
        "taxa_atraso": "Taxa de atraso (%)",
    },
)

fig_distancia.update_traces(
    textposition="outside"
)

fig_distancia.update_layout(
    template="plotly_white",
    yaxis_range=[0, 55],
)

st.subheader("Taxa de atraso por distância")

st.plotly_chart(
    fig_distancia,
    use_container_width=True
)


# ==========================================
# 8. SIMULADOR DE RISCO COM MACHINE LEARNING
# ==========================================

st.divider()

st.title("🤖 Simulador de risco de atraso")

st.write(
    "Informe as características de um pedido "
    "para estimar seu risco de atraso."
)

with st.form("formulario_previsao"):

    col1, col2 = st.columns(2)

    with col1:

        distancia = st.number_input(
            "Distância (km)",
            min_value=0,
            max_value=10000,
            value=1500,
            step=100,
        )

        volume = st.number_input(
            "Volume da transportadora",
            min_value=0,
            max_value=1000000,
            value=300,
        )

        prazo = st.number_input(
            "Prazo previsto (dias)",
            min_value=1,
            max_value=365,
            value=5,
        )

    with col2:

        regiao = st.selectbox(
            "Região",
            [
                "Sudeste",
                "Sul",
                "Nordeste",
                "Norte",
                "Centro-Oeste",
            ],
        )

        transportadora = st.selectbox(
            "Transportadora",
            [
                "TransLog A",
                "TransLog B",
                "TransLog C",
            ],
        )

        periodo_pico = st.selectbox(
            "Período de pico?",
            options=[0, 1],
            format_func=lambda x: (
                "Sim" if x == 1 else "Não"
            ),
        )

    enviar = st.form_submit_button(
        "Calcular risco de atraso",
        use_container_width=True,
    )


if enviar:

    dados_pedido = {
        "distancia_km": int(distancia),
        "volume_transportadora": int(volume),
        "periodo_pico": int(periodo_pico),
        "prazo_previsto_dias": int(prazo),
        "regiao": regiao,
        "transportadora": transportadora,
    }

    try:

        resposta = requests.post(
            "http://127.0.0.1:8000/prever",
            json=dados_pedido,
            timeout=10,
        )

        resposta.raise_for_status()

        resultado = resposta.json()

        st.subheader("Resultado da previsão")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Previsão",
            resultado["previsao"],
        )

        col2.metric(
            "Probabilidade de atraso",
            f'{resultado["probabilidade_atraso"]:.2f}%',
        )

        col3.metric(
            "Nível de risco",
            resultado["nivel_risco"],
        )

        if resultado["nivel_risco"] == "Alto":
            st.error("O pedido apresenta alto risco estimado de atraso.")

        elif resultado["nivel_risco"] == "Moderado":
            st.warning("O pedido apresenta risco moderado estimado de atraso.")

        else:
            st.success("O pedido apresenta baixo risco estimado de atraso.")

        st.caption(resultado["aviso"])

    except requests.exceptions.ConnectionError:
        st.error(
            "Não foi possível conectar à API. "
            "Verifique se o servidor FastAPI está executando."
        )

    except requests.exceptions.Timeout:
        st.error("A API demorou demais para responder.")

    except requests.exceptions.HTTPError:
        st.error(
            f"Erro retornado pela API: {resposta.status_code}"
        )

    except (ValueError, KeyError):
        st.error("A API retornou uma resposta inválida.")


# ==========================================
# 9. RODAPÉ
# ==========================================

st.divider()

st.caption(
    "PulseOps AI | Análise de dados e previsão de atrasos "
    "| Projeto educacional com dados sintéticos."
)
