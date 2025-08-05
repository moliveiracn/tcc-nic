"""
config.py

Módulo de configuração central para caminhos do projeto.
Utiliza pathlib para garantir compatibilidade entre sistemas operacionais
e centraliza as definições de diretórios para fácil manutenção.

Este módulo também garante que os diretórios de saída de dados processados
e gráficos sejam criados automaticamente se ainda não existirem.
"""

from pathlib import Path

# --- Caminho Raiz ---
# Define o diretório raiz do projeto de forma dinâmica.
# Path(__file__) -> caminho deste arquivo
# .resolve()    -> resolve o caminho absoluto (ex: C:\Users\...)
# .parent       -> sobe um nível na hierarquia (a pasta do projeto)
ROOT: Path = Path(__file__).resolve().parent

# --- Diretórios de Dados ---
# Define os caminhos para dados brutos e processados.
DATA_RAW: Path = ROOT / "data" / "raw"
DATA_PROCESSED: Path = ROOT / "data" / "processed"

# --- Diretório de Saídas ---
# Define o caminho para salvar os gráficos gerados.
GRAPH_OUTPUT: Path = ROOT / "output" / "graphs"

# --- Garantia de Existência dos Diretórios ---
# Cria os diretórios de saída para evitar FileNotFoundError em outros scripts.
# exist_ok=True -> não gera erro se o diretório já existir.
# parents=True  -> cria diretórios pais se necessário (ex: /output/ se não existir).
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
GRAPH_OUTPUT.mkdir(parents=True, exist_ok=True)