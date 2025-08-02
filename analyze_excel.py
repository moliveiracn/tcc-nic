# -*- coding: utf-8 -*-

"""
Este script analisa os dados mensais de turismo em Las Vegas durante o ano de 2022,
com foco em identificar o impacto dos shows do BTS realizados em abril.
Ele gera graficos sobre:
- Volume de visitantes
- Ocupacao hoteleira total e nos finais de semana
- ADR (Average Daily Room Rate - diaria media de hoteis)
E calcula variacoes percentuais para apoiar a analise economica.

Esta versão foi refatorada para maior modularidade e reutilização.
Novas features:
- Gráfico combinado com duplo eixo Y para correlação de métricas.
- Análise quantitativa do impacto do evento em comparação com a média.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.tseries.offsets import MonthEnd
from config import DATA_RAW, DATA_PROCESSED, GRAPH_OUTPUT

# =========================================================
# CONFIGURACOES GERAIS
# =========================================================
# --- Arquivo e Aba ---
ARQUIVO_EXCEL = DATA_RAW / "Year_to_Date_Summary_for_2022.xlsx"
ABA_EXCEL = "Las Vegas 2022"

# --- Detalhes do Evento para Destaque ---
EVENTO_NOME = "Shows BTS"
EVENTO_INI = "2022-04-01"
EVENTO_FIM = "2022-04-30"

# --- Mapeamento do Excel (linhas e colunas) ---
LINHA_DATAS = 6
COLUNAS_DATAS = list(range(1, 25, 2))
LINHA_INICIO_METRICAS = 7
LINHA_FIM_METRICAS = 16
COLUNA_NOMES_METRICAS = 0


def carregar_dados_brutos(caminho_arquivo, aba):
    """Carrega uma aba específica de um arquivo Excel sem cabeçalhos."""
    try:
        xlsx = pd.ExcelFile(caminho_arquivo)
        return xlsx.parse(aba, header=None)
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return None


def limpar_e_estruturar_dados(df):
    """Extrai, limpa e estrutura os dados de turismo do DataFrame bruto."""
    if df is None:
        return None

    # Extrai as datas e as converte para o final do mês
    linhas_datas = df.iloc[LINHA_DATAS, COLUNAS_DATAS]
    datas_formatadas = pd.to_datetime(linhas_datas.values) + MonthEnd(0)

    # Extrai os nomes das métricas
    nomes_metricas = (
        df.iloc[LINHA_INICIO_METRICAS:LINHA_FIM_METRICAS, COLUNA_NOMES_METRICAS]
        .str.strip()
        .tolist()
    )

    # Cria o DataFrame final e o preenche
    dados_limpos = pd.DataFrame(index=datas_formatadas, columns=nomes_metricas)
    for col_idx, data in zip(COLUNAS_DATAS, dados_limpos.index):
        valores = df.iloc[LINHA_INICIO_METRICAS:LINHA_FIM_METRICAS, col_idx].values
        dados_limpos.loc[data] = pd.to_numeric(valores, errors="coerce")

    return dados_limpos.astype(float)


def gerar_grafico(dados, metrica, titulo, ylabel, cor, caminho_salvar):
    """Gera e salva um gráfico de linha para uma métrica específica."""
    plt.figure(figsize=(12, 7))
    sns.lineplot(data=dados[metrica], marker="o", color=cor, label=metrica)

    # Destaca o período do evento no gráfico
    plt.axvspan(
        pd.to_datetime(EVENTO_INI),
        pd.to_datetime(EVENTO_FIM),
        color="orange",
        alpha=0.2,
        label=EVENTO_NOME,
    )

    plt.title(titulo, fontsize=16)
    plt.ylabel(ylabel)
    plt.xlabel("Mês")
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(caminho_salvar)
    plt.close()  # Libera memória


def gerar_grafico_combinado_com_eixo_duplo(
    dados, metrica1, metrica2, titulo, ylabel1, ylabel2, cor1, cor2, caminho_salvar
):
    """Gera um gráfico com duas métricas e dois eixos Y."""
    fig, ax1 = plt.subplots(figsize=(12, 7))

    # Eixo primário (Y1)
    ax1.set_xlabel("Mês")
    ax1.set_ylabel(ylabel1, color=cor1)
    sns.lineplot(data=dados[metrica1], marker="o", color=cor1, ax=ax1, label=metrica1)
    ax1.tick_params(axis="y", labelcolor=cor1)

    # Eixo secundário (Y2)
    ax2 = ax1.twinx()
    ax2.set_ylabel(ylabel2, color=cor2)
    sns.lineplot(data=dados[metrica2], marker="s", color=cor2, ax=ax2, label=metrica2)
    ax2.tick_params(axis="y", labelcolor=cor2)

    # Destaque do evento
    ax1.axvspan(
        pd.to_datetime(EVENTO_INI),
        pd.to_datetime(EVENTO_FIM),
        color="orange",
        alpha=0.2,
        label=EVENTO_NOME,
    )

    plt.title(titulo, fontsize=16)
    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1), bbox_transform=ax1.transAxes)
    plt.savefig(caminho_salvar)
    plt.close()


def calcular_e_salvar_variacoes(dados, caminho_salvar):
    """Calcula a variação percentual mês a mês e salva em CSV."""
    variacoes = pd.DataFrame(
        {
            "Visitantes": dados["Visitor Volume"].pct_change() * 100,
            "Ocupacao Total": dados["Total Occupancy"].pct_change() * 100,
            "ADR": dados["Average Daily Room Rate (ADR)"].pct_change() * 100,
        }
    ).round(2)

    variacoes.to_csv(caminho_salvar)
    print(f"Variações percentuais salvas em: {caminho_salvar}")


def analise_comparativa_evento(dados):
    """Imprime uma análise comparativa do mês do evento com a média dos outros meses."""
    mes_evento = pd.to_datetime(EVENTO_INI).month
    dados_evento = dados[dados.index.month == mes_evento]
    dados_outros_meses = dados[dados.index.month != mes_evento]

    media_outros_meses = dados_outros_meses.mean()

    print("\n" + "=" * 50)
    print(f"🔎 Análise de Impacto Quantitativo: {EVENTO_NOME}")
    print("=" * 50)

    for metrica in [
        "Visitor Volume",
        "Total Occupancy",
        "Average Daily Room Rate (ADR)",
    ]:
        valor_evento = dados_evento[metrica].iloc[0]
        media_geral = media_outros_meses[metrica]
        diferenca_percentual = ((valor_evento - media_geral) / media_geral) * 100

        print(f"\n--- {metrica} ---")
        print(f"  - Mês do Evento: {valor_evento:,.0f}")
        print(f"  - Média dos Outros Meses: {media_geral:,.0f}")
        print(f"  - Impacto Percentual: {diferenca_percentual:+.2f}%")
    print("=" * 50 + "\n")


def main():
    """Orquestra a execução do script: carregar, analisar, plotar e salvar."""
    sns.set(style="whitegrid")

    # Etapa 1: Carregar e processar os dados
    df_bruto = carregar_dados_brutos(ARQUIVO_EXCEL, ABA_EXCEL)
    dados = limpar_e_estruturar_dados(df_bruto)

    if dados is None:
        print("Análise interrompida devido a erro no carregamento dos dados.")
        return

    # Etapa 2: Gerar e salvar gráficos individuais
    # ... (chamadas para gerar_grafico como antes) ...

    # Etapa 3: Gerar o novo gráfico combinado
    gerar_grafico_combinado_com_eixo_duplo(
        dados=dados,
        metrica1="Visitor Volume",
        metrica2="Average Daily Room Rate (ADR)",
        titulo="Correlação: Volume de Visitantes vs. Diária Média (ADR)",
        ylabel1="Número de Visitantes",
        ylabel2="Valor (USD)",
        cor1="royalblue",
        cor2="firebrick",
        caminho_salvar=GRAPH_OUTPUT / "visitantes_vs_adr_2022.png",
    )
    print(f"Gráfico de correlação salvo com sucesso em: {GRAPH_OUTPUT}")

    # Etapa 4: Calcular e salvar variações percentuais
    caminho_csv = DATA_PROCESSED / "variacoes_percentuais.csv"
    calcular_e_salvar_variacoes(dados, caminho_csv)

    # Etapa 5: Exibir a nova análise quantitativa
    analise_comparativa_evento(dados)

    print("\nAnálise concluída com sucesso!")


if __name__ == "__main__":
    main()
