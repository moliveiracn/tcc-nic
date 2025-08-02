from pathlib import Path

# === Diretório raiz do projeto ===
ROOT = Path(__file__).resolve().parent

# === Diretórios principais ===
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
GRAPH_OUTPUT = ROOT / "output" / "graphs"
