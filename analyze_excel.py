# -*- coding: utf-8 -*-

"""
Este script analisa os dados mensais de turismo em Las Vegas durante o ano de 2022,
com foco em identificar o impacto dos shows do BTS realizados em abril.
Ele gera graficos sobre:
- Volume de visitantes
- Ocupacao hoteleira total e nos finais de semana
- ADR (Average Daily Rate - diaria media de hoteis)
E calcula variacoes percentuais para apoiar a analise economica.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from pandas.tseries.offsets import MonthEnd
from config import (
    DATA_RAW,
    DATA_PROCESSED,
    GRAPH_OUTPUT
)

# =========================================================
# CONFIGURACOES INICIAIS
# =========================================================
ARQUIVO_EXCEL = DATA_RAW / "Year_to_Date_Summary_for_2022.xlsx"
ABA = "Las Vegas 2022"  # ou "Laughlin 2022", "Mesquite 2022"

# =========================================================
# ETAPA 1 - Carregar o Excel bruto, sem cabecalhos fixos
# =========================================================
xlsx = pd.ExcelFile(ARQUIVO_EXCEL)
df = xlsx.parse(ABA, header=None)  # nao usamos header pois os dados estao misturados

# =========================================================
# ETAPA 2 - Identificar colunas com datas validas (meses)
# =========================================================
# Os dados estao nas colunas impares (1, 3, 5, ..., 23),
# e as datas estao na linha 6 (index 6)
colunas_validas = list(range(1, 25, 2))
linhas_datas = df.iloc[6, colunas_validas]

# Converter para datetime e corrigir para o fim do mes
datas_filtradas = pd.to_datetime(linhas_datas.values) + MonthEnd(0)

# =========================================================
# ETAPA 3 - Extrair nomes das metricas e valores mensais
# =========================================================
# As metricas estao na coluna 0, linhas 7 a 15 (inclusive)
lin_inicio = 7
lin_fim = 16
metricas = df.iloc[lin_inicio:lin_fim, 0].str.strip().tolist()

# Criar DataFrame limpo com as datas como indice e metricas como colunas
dados = pd.DataFrame(index=datas_filtradas, columns=metricas)

# Preencher os dados percorrendo as colunas
for col_i, data in zip(colunas_validas, dados.index):
    valores = df.iloc[lin_inicio:lin_fim, col_i].values
    dados.loc[data] = pd.to_numeric(valores, errors='coerce')

# Converter tudo para float
dados = dados.astype(float)

# =========================================================
# ETAPA 4 - Gerar graficos com destaque para abril (shows do BTS)
# =========================================================
sns.set(style="whitegrid")

# GRAFICO 1: Visitantes por mes
plt.figure(figsize=(10, 6))
sns.lineplot(data=dados["Visitor Volume"], marker='o')
plt.axvspan(pd.to_datetime("2022-04-01"), pd.to_datetime("2022-04-30"), color='orange', alpha=0.2, label='Shows BTS')
plt.title("Volume de Visitantes - Las Vegas 2022")
plt.ylabel("Visitantes")
plt.xlabel("Mes")
plt.legend()
plt.tight_layout()
plt.savefig(GRAPH_OUTPUT / "visitantes_2022.png")

# GRAFICO 2: Ocupacao total e aos finais de semana
plt.figure(figsize=(10, 6))
sns.lineplot(data=dados[["Total Occupancy", "Weekend Occupancy"]], marker='o')
plt.axvspan(pd.to_datetime("2022-04-01"), pd.to_datetime("2022-04-30"), color='orange', alpha=0.2, label='Shows BTS')
plt.title("Ocupacao Hoteleira - Las Vegas 2022")
plt.ylabel("Taxa de Ocupacao")
plt.xlabel("Mes")
plt.legend()
plt.tight_layout()
plt.savefig(GRAPH_OUTPUT / "ocupacao_2022.png")

# GRAFICO 3: ADR (diaria media)
plt.figure(figsize=(10, 6))
sns.lineplot(data=dados["Average Daily Room Rate (ADR)"], marker='o', color='green')
plt.axvspan(pd.to_datetime("2022-04-01"), pd.to_datetime("2022-04-30"), color='orange', alpha=0.2, label='Shows BTS')
plt.title("ADR (Diaria Media) - Las Vegas 2022")
plt.ylabel("USD")
plt.xlabel("Mes")
plt.legend()
plt.tight_layout()
plt.savefig(GRAPH_OUTPUT / "adr_2022.png")

# =========================================================
# ETAPA 5 - Calcular variacao percentual mes-a-mes
# =========================================================
variacoes = pd.DataFrame({
    "Visitantes": dados["Visitor Volume"].pct_change() * 100,
    "Ocupacao Total": dados["Total Occupancy"].pct_change() * 100,
    "ADR": dados["Average Daily Room Rate (ADR)"].pct_change() * 100
}).round(2)

# Salvar como CSV para uso no TCC
variacoes.to_csv(DATA_PROCESSED / "variacoes_percentuais.csv")
print("Graficos e variacoes salvos com sucesso.")