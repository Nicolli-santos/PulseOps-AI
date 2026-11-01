
import os
import random

import mysql.connector
import pandas as pd

# ============================================================
# PULSEOPS AI
# Simulador de pedidos e atrasos de entrega
#
# IMPORTANTE:
# Todos os dados são sintéticos.
# Não representam pedidos ou entregas reais de empresas.
# ============================================================

random.seed(42)

QUANTIDADE_PEDIDOS = 10_000
NOME_ARQUIVO = "dados_pedidos_sinteticos.csv"

REGIOES = [
    "Norte",
    "Nordeste",
    "Centro-Oeste",
    "Sudeste",
    "Sul",
]

TRANSPORTADORAS = [
    "TransLog A",
    "TransLog B",
    "TransLog C",
]


def gerar_pedidos():
    """Gera a base sintética de pedidos."""

    pedidos = []
    data_inicial = pd.Timestamp("2025-01-01")

    for i in range(QUANTIDADE_PEDIDOS):
        pedido_id = f"PED{i + 1:05d}"

        data_compra = (
            data_inicial
            + pd.Timedelta(days=random.randint(0, 364))
        )

        distancia_km = random.randint(20, 2500)
        regiao = random.choice(REGIOES)
        transportadora = random.choice(TRANSPORTADORAS)
        volume_transportadora = random.randint(50, 500)
        periodo_pico = random.choice([0, 1])
        prazo_previsto_dias = random.randint(3, 15)

        data_entrega_prevista = (
            data_compra
            + pd.Timedelta(days=prazo_previsto_dias)
        )

        probabilidade_atraso = (
            0.08
            + distancia_km / 10000
            + volume_transportadora / 2500
            + periodo_pico * 0.12
        )

        probabilidade_atraso = min(
            probabilidade_atraso,
            0.85,
        )

        atrasado = int(
            random.random() < probabilidade_atraso
        )

        if atrasado == 1:
            dias_variacao = random.randint(1, 7)
            status = "atrasado"
        else:
            dias_variacao = random.randint(-2, 0)
            status = "entregue_no_prazo"

        data_entrega_real = (
            data_entrega_prevista
            + pd.Timedelta(days=dias_variacao)
        )

        pedidos.append({
            "pedido_id": pedido_id,
            "data_compra": data_compra,
            "data_entrega_prevista": data_entrega_prevista,
            "data_entrega_real": data_entrega_real,
            "status": status,
            "distancia_km": distancia_km,
            "regiao": regiao,
            "transportadora": transportadora,
            "volume_transportadora": volume_transportadora,
            "periodo_pico": periodo_pico,
            "prazo_previsto_dias": prazo_previsto_dias,
            "atrasado": atrasado,
        })

    return pd.DataFrame(pedidos)


def verificar_dados(df):
    """Verifica condições básicas da base."""

    assert len(df) == QUANTIDADE_PEDIDOS
    assert df["pedido_id"].is_unique
    assert df["atrasado"].isin([0, 1]).all()
    assert not df.isnull().values.any()

    assert (
        (df["status"] == "atrasado")
        == (df["atrasado"] == 1)
    ).all()

    assert (
        (df["data_entrega_real"] > df["data_entrega_prevista"])
        == (df["atrasado"] == 1)
    ).all()

    assert (
        df["data_entrega_real"] >= df["data_compra"]
    ).all()


def salvar_csv(df):
    """Salva a base sintética em CSV."""

    df.to_csv(
        NOME_ARQUIVO,
        index=False,
        encoding="utf-8",
    )

    print(f"\nArquivo CSV salvo: {NOME_ARQUIVO}")


def importar_para_mysql(df):
    """Insere os pedidos no MySQL, sem duplicar a base."""

    senha_mysql = os.getenv("MYSQL_PASSWORD")

    if not senha_mysql:
        raise ValueError(
            "A variável MYSQL_PASSWORD não foi encontrada. "
            "Configure a senha no terminal do VS Code."
        )

    conexao = None
    cursor = None

    try:
        conexao = mysql.connector.connect(
            host="127.0.0.1",
            port=3307,
            user="root",
            password=senha_mysql,
            database="pulseops_ai",
        )

        cursor = conexao.cursor()

        # Segurança: não importar se já houver registros.
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_existente = cursor.fetchone()[0]

        if total_existente > 0:
            print(
                "\nIMPORTAÇÃO CANCELADA: a tabela pedidos "
                f"já contém {total_existente} registros."
            )
            print(
                "Nenhum pedido foi inserido. "
                "Verifique a tabela antes de continuar."
            )
            return

        comando_sql = """
            INSERT INTO pedidos (
                pedido_id,
                data_compra,
                data_entrega_prevista,
                data_entrega_real,
                status,
                distancia_km,
                regiao,
                transportadora,
                volume_transportadora,
                periodo_pico,
                prazo_previsto_dias,
                atrasado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        colunas = [
            "pedido_id",
            "data_compra",
            "data_entrega_prevista",
            "data_entrega_real",
            "status",
            "distancia_km",
            "regiao",
            "transportadora",
            "volume_transportadora",
            "periodo_pico",
            "prazo_previsto_dias",
            "atrasado",
        ]

        dados = []

        for linha in df[colunas].itertuples(
            index=False,
            name=None,
        ):
            registro = list(linha)

            # Converter datas do pandas para datetime do Python.
            for indice in (1, 2, 3):
                registro[indice] = registro[indice].to_pydatetime()

            dados.append(tuple(registro))

        cursor.executemany(comando_sql, dados)
        conexao.commit()

        cursor.execute("SELECT COUNT(*) FROM pedidos")
        total_final = cursor.fetchone()[0]

        print("\nIMPORTAÇÃO CONCLUÍDA")
        print("-" * 40)
        print("Pedidos inseridos:", cursor.rowcount)
        print("Total de pedidos na tabela:", total_final)

        if total_final != QUANTIDADE_PEDIDOS:
            print(
                "ATENÇÃO: a quantidade final difere "
                "da quantidade esperada."
            )

    except Exception:
        if conexao is not None and conexao.is_connected():
            conexao.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        if conexao is not None and conexao.is_connected():
            conexao.close()


def main():
    print("=" * 60)
    print("PULSEOPS AI - BASE SINTÉTICA")
    print("=" * 60)

    df = gerar_pedidos()
    verificar_dados(df)
    salvar_csv(df)

    print("\nVERIFICAÇÃO DOS DADOS")
    print("-" * 40)
    print("Total de pedidos:", len(df))
    print("IDs únicos:", df["pedido_id"].nunique())
    print("Total de colunas:", len(df.columns))
    print("Valores ausentes:", int(df.isnull().sum().sum()))
    print("Pedidos atrasados:", int(df["atrasado"].sum()))
    print(
        "Percentual sintético de atrasos:",
        f"{df['atrasado'].mean() * 100:.2f}%",
    )

    print("\nPrimeiros cinco pedidos:")
    print(df.head().to_string(index=False))

    print("\nDistribuição dos status:")
    print(df["status"].value_counts().to_string())

    print(
        "\nAVISO: os dados são sintéticos e servem "
        "para fins educacionais e de demonstração."
    )

    importar_para_mysql(df)


if __name__ == "__main__":
    main()
