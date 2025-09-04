"""
preprocess_vegas_data.py

Este script é responsável pela etapa de ETL (Extract, Transform, Load).
Ele lê múltiplos arquivos Excel brutos da LVCVA, cada um contendo dados
de turismo de Las Vegas para um ano específico.

O processo consiste em:
1. Encontrar todos os arquivos de dados anuais na pasta `DATA_RAW`.
2. Para cada arquivo, extrair as métricas e datas usando uma estrutura similar
   à do script `analyze_excel.py` original.
3. Unificar todos os dados em um único DataFrame do Pandas.
4. Salvar o resultado como um único arquivo CSV limpo e padronizado na
   pasta `DATA_PROCESSED`, pronto para a análise.

O arquivo de saída ('vegas_tourism_yearly.csv') terá uma estrutura "tidy",
facilitando a análise e a plotagem de gráficos comparativos.
"""

import pandas as pd
from pathlib import Path
import re
from typing import Optional

from config import DATA_RAW, DATA_PROCESSED

# Mapeamento das colunas e linhas nos arquivos Excel.
# Assumimos que a estrutura é consistente entre os anos.
LINHA_DATAS = 6
COLUNAS_DATAS = list(range(1, 25, 2))
COLUNA_NOMES_METRICAS = 0
ABA_EXCEL = "Las Vegas "  # Assumindo que o nome da aba é consistente
# Palavras que indicam o início de um rodapé e, portanto, o fim das métricas
FOOTER_KEYWORDS = [FOOTER_KEYWORDS = [FOOTER_KEYWORDS = ["source", "nota", "notes"]]]


def detect_metric_bounds(df: pd.DataFrame) -> tuple[int, int]:
    """
    Detecta as linhas de início e fim das métricas em um DataFrame bruto.

    A busca começa logo após a linha de datas (`LINHA_DATAS`) e segue até
    encontrar uma linha vazia ou um texto que indique rodapé (por exemplo,
    "Source"). O índice final retornado é exclusivo, compatível com slicing
    do pandas.
    """

    start_row = LINHA_DATAS + 1
    # Avança até encontrar a primeira linha com valor na coluna de nomes
    while start_row < len(df):
        cell = df.iloc[start_row, COLUNA_NOMES_METRICAS]
        if pd.isna(cell) or (isinstance(cell, str) and cell.strip() == ""):
            start_row += 1
            continue
        break

    end_row = start_row
    while end_row < len(df):
        cell = df.iloc[end_row, COLUNA_NOMES_METRICAS]

        # Fim quando célula vazia ou linha toda vazia
        if pd.isna(cell) or (isinstance(cell, str) and cell.strip() == "") or df.iloc[end_row].isna().all():
            break

        # Fim quando rodapé conhecido é encontrado
        if isinstance(cell, str) and cell.strip().lower().startswith(tuple(FOOTER_KEYWORDS)):
            break

        end_row += 1

    return start_row, end_row

def extract_year_from_filename(path: Path) -> Optional[int]:
    """Extrai o ano do nome do arquivo (ex: 'data_2022.xlsx' -> 2022)."""
    match = re.search(r"\b(19|20)\d{2}\b", path.stem)
    if match:
        return int(match.group())
    print(f"Aviso: Não foi possível extrair o ano do arquivo {path.name}. Ignorando.")
    return None

def process_single_file(file_path: Path, year: int) -> Optional[pd.DataFrame]:
    """Carrega e processa um único arquivo Excel, retornando um DataFrame limpo."""
    try:
        df_raw = pd.read_excel(file_path, sheet_name=ABA_EXCEL + str(year), header=None)
    except Exception as e:
        print(f"Erro ao ler o arquivo {file_path.name}: {e}")
        return None

    # Detecta dinamicamente o intervalo das métricas
    start_row, end_row = detect_metric_bounds(df_raw)
    df_metrics = df_raw.iloc[start_row:end_row]

    # Extrai nomes das métricas e formata
    metric_names = df_metrics.iloc[:, COLUNA_NOMES_METRICAS].astype(str).str.strip().tolist()

    # Extrai valores mensais
    monthly_data = df_metrics.iloc[:, COLUNAS_DATAS].T
    monthly_data.columns = metric_names
    
    # Limpa e converte para numérico
    for col in monthly_data.columns:
        monthly_data[col] = pd.to_numeric(monthly_data[col], errors='coerce')

    # Adiciona data (mês e ano)
    monthly_data['Year'] = year
    monthly_data['Month'] = range(1, len(monthly_data) + 1)
    
    return monthly_data.dropna(how='all')

def main():
    """
    Função principal que orquestra a leitura, processamento e salvamento dos dados.
    """
    print("Iniciando pré-processamento dos dados de turismo de Las Vegas...")
    
    source_files = list(DATA_RAW.glob("*.xlsx"))
    if not source_files:
        print("Nenhum arquivo Excel (.xlsx) encontrado em data/raw/. Encerrando.")
        return

    all_data = []
    for file in source_files:
        year = extract_year_from_filename(file)
        if year:
            print(f"Processando arquivo: {file.name} para o ano {year}...")
            df_year = process_single_file(file, year)
            if df_year is not None:
                all_data.append(df_year)

    if not all_data:
        print("Nenhum dado foi processado com sucesso. Encerrando.")
        return
        
    # Concatena todos os DataFrames em um só
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Cria uma coluna de data completa para facilitar a plotagem
    final_df['Date'] = pd.to_datetime(final_df['Year'].astype(str) + '-' + final_df['Month'].astype(str) + '-01')
    final_df = final_df.set_index('Date')

    # Salva o arquivo CSV final
    output_path = DATA_PROCESSED / "vegas_tourism_yearly.csv"
    final_df.to_csv(output_path)
    
    print("-" * 50)
    print(f"✅ Processamento concluído!")
    print(f"Dados de {len(final_df['Year'].unique())} anos foram consolidados.")
    print(f"Arquivo de saída salvo em: {output_path}")
    print("-" * 50)

if __name__ == "__main__":
    main()
