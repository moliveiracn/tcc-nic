"""
analyze_excel.py (Refatorado)

Este script analisa os dados de turismo em Las Vegas, já pré-processados,
para identificar o impacto dos shows do BTS em abril de 2022.

O fluxo de trabalho é:
1. Carregar o arquivo CSV consolidado de 'data/processed'.
2. Gerar gráficos comparativos que mostram a evolução das métricas ao
   longo dos anos, permitindo uma análise visual do impacto do evento
   em relação a outros períodos.
3. Calcular e exibir estatísticas comparativas.

A refatoração tornou este script focado apenas na análise e visualização,
removendo a complexidade do tratamento de dados brutos.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import DATA_PROCESSED, GRAPH_OUTPUT

# --- Constantes de Análise ---
PROCESSED_DATA_FILE = DATA_PROCESSED / "vegas_tourism_yearly.csv"
EVENT_NAME = "Shows BTS"
EVENT_YEAR = 2022
EVENT_MONTH = 4

def load_data() -> pd.DataFrame:
    """Carrega os dados processados e prepara o índice."""
    try:
        df = pd.read_csv(PROCESSED_DATA_FILE, parse_dates=['Date'], index_col='Date')
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo de dados processado não encontrado em {PROCESSED_DATA_FILE}")
        print("Por favor, execute o script 'preprocess_vegas_data.py' primeiro.")
        return None

def plot_yearly_comparison(df: pd.DataFrame, metric: str, title: str, ylabel: str):
    """
    Gera um gráfico de linha comparando uma métrica ao longo dos meses
    para cada ano disponível nos dados.
    """
    plt.figure(figsize=(14, 8))
    
    # Usa pivot para ter anos como colunas e meses como linhas
    df_pivot = df.pivot_table(index=df.index.month, columns=df.index.year, values=metric)
    
    sns.lineplot(data=df_pivot, markers=True, dashes=False)

    # Destaque para o ponto do evento (Abril de 2022)
    event_value = df_pivot.loc[EVENT_MONTH, EVENT_YEAR]
    plt.scatter(EVENT_MONTH, event_value, color='red', s=150, zorder=5, label=f"{EVENT_NAME} ({EVENT_YEAR})")
    
    plt.title(title, fontsize=16)
    plt.ylabel(ylabel)
    plt.xlabel("Mês")
    plt.xticks(ticks=range(1, 13), labels=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])
    plt.legend(title="Ano")
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    filename = GRAPH_OUTPUT / f"comparison_{metric.replace(' ', '_').lower()}.png"
    plt.savefig(filename)
    plt.close()
    print(f"Gráfico salvo em: {filename}")

def comparative_analysis(df: pd.DataFrame):
    """Imprime uma análise comparativa do mês do evento."""
    print("\n" + "="*60)
    print(f"🔎 Análise de Impacto Quantitativo: {EVENT_NAME} (Abril de {EVENT_YEAR})")
    print("="*60)

    # Filtra dados do evento
    event_data = df[(df.index.year == EVENT_YEAR) & (df.index.month == EVENT_MONTH)]
    
    # Filtra dados para o mesmo mês em outros anos
    april_other_years = df[(df.index.month == EVENT_MONTH) & (df.index.year != EVENT_YEAR)]

    for metric in ["Visitor Volume", "Total Occupancy", "Average Daily Room Rate (ADR)"]:
        if metric not in df.columns: continue

        event_value = event_data[metric].iloc[0]
        avg_april_others = april_other_years[metric].mean()
        
        diff_vs_other_aprils = ((event_value - avg_april_others) / avg_april_others) * 100

        print(f"\n--- {metric} ---")
        print(f"  - Valor em Abr/2022: {event_value:,.2f}")
        print(f"  - Média de Abril (outros anos): {avg_april_others:,.2f}")
        print(f"  - Impacto vs. outros Abrils: {diff_vs_other_aprils:+.2f}%")
    print("="*60 + "\n")

def main():
    """Orquestra a análise e geração de gráficos."""
    sns.set(style="whitegrid", palette="viridis")
    
    df = load_data()
    if df is None:
        return

    # Gerar gráficos comparativos para as principais métricas
    plot_yearly_comparison(
        df,
        metric="Visitor Volume",
        title="Comparativo Anual do Volume de Visitantes em Las Vegas",
        ylabel="Número de Visitantes"
    )
    plot_yearly_comparison(
        df,
        metric="Total Occupancy",
        title="Comparativo Anual da Ocupação Hoteleira Total (%)",
        ylabel="Ocupação (%)"
    )
    plot_yearly_comparison(
        df,
        metric="Average Daily Room Rate (ADR)",
        title="Comparativo Anual da Diária Média (ADR)",
        ylabel="Valor (USD)"
    )

    # Realizar e imprimir a análise quantitativa
    comparative_analysis(df)
    
    print("Análise concluída com sucesso!")

if __name__ == "__main__":
    main()