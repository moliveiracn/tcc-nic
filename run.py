import argparse
import pandas as pd
from config import DATA_PROCESSED


def run_fetch_artists(args):
    print("▶️ Executando o módulo 'artists_info'...")
    from artists_info import get_artist_raw_data
    raw_data = get_artist_raw_data()
    df = pd.DataFrame(raw_data)
    output_path = DATA_PROCESSED / "artists_data.csv"
    df.to_csv(output_path, index=False, sep=";")
    print(f"✅ Dados de artistas salvos em: {output_path}")


def run_fetch_flights(args):
    print("▶️ Executando o módulo 'flights_parser'...")
    from flights_parser import get_flight_raw_data, HEADER
    raw_data = get_flight_raw_data(max_lines=args.max_lines)
    output_path = DATA_PROCESSED / "flights_data.csv"
    df = pd.DataFrame(raw_data, columns=HEADER)
    df.to_csv(output_path, index=False, sep=";")
    print(f"✅ Dados de voos salvos em: {output_path}")


def run_fetch_reddit(args):
    print("▶️ Executando o módulo 'reddit_scraper'...")
    from reddit_scraper import get_reddit_raw_data
    raw_data = get_reddit_raw_data(post_limit=args.post_limit, comment_limit=args.comment_limit)
    df = pd.DataFrame(raw_data)
    output_path = DATA_PROCESSED / "reddit_comments.csv"
    df.to_csv(output_path, index=False, sep=";")
    print(f"✅ Dados do Reddit salvos em: {output_path}")


def run_preprocess_vegas(args):
    print("▶️ Executando o pré-processamento dos dados de Las Vegas...")
    from preprocess_data import main as preprocess_main
    preprocess_main()


def run_analyze_vegas(args):
    print("▶️ Executando a análise dos dados de Las Vegas...")
    from analyze_processed_data import main as analyze_main
    analyze_main(metrics=args.metrics)


def main():
    """Ponto de entrada principal para coletar, processar e analisar dados.

    Uso:
        python run.py <modulo> [opções]

    Exemplos:
        python run.py preprocess
        python run.py excel --metrics Visitors

        # Coleta de dados
        python run.py fetch-artists
        python run.py fetch-flights --max-lines 100000
        python run.py fetch-reddit --post-limit 10 --comment-limit 5

        # Processamento e Análise
        python run.py preprocess-vegas
        python run.py analyze-vegas --metrics "Visitors" "Average Room Rate"
    """
    parser = argparse.ArgumentParser(
        description="Orquestrador de scripts do projeto TCC.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="module", required=True)

    # --- Subparsers de Coleta (Fetch) ---
    fetch_artists_parser = subparsers.add_parser(
        "fetch-artists", help="Coleta dados de artistas (Spotify, Last.fm, etc.)."
    )
    fetch_artists_parser.set_defaults(func=run_fetch_artists)

    fetch_flights_parser = subparsers.add_parser(
        "fetch-flights", help="Processa arquivos brutos de voos para chegadas em LAS."
    )
    fetch_flights_parser.add_argument("--max-lines", type=int, default=None, help="Número máximo de linhas por arquivo para processar.")
    fetch_flights_parser.set_defaults(func=run_fetch_flights)

    fetch_reddit_parser = subparsers.add_parser(
        "fetch-reddit", help="Coleta comentários do Reddit."
    )
    fetch_reddit_parser.add_argument("--post-limit", type=int, default=50, help="Máximo de posts por par de termos.")
    fetch_reddit_parser.add_argument("--comment-limit", type=int, default=20, help="Máximo de comentários por post.")
    fetch_reddit_parser.set_defaults(func=run_fetch_reddit)

    # --- Subparsers de Processamento e Análise ---
    preprocess_vegas_parser = subparsers.add_parser(
        "preprocess-vegas", help="Consolida e padroniza os dados de turismo de Las Vegas a partir dos arquivos Excel."
    )
    preprocess_vegas_parser.set_defaults(func=run_preprocess_vegas)

    analyze_vegas_parser = subparsers.add_parser(
        "analyze-vegas",
        help="Analisa dados de turismo de Las Vegas e gera gráficos.",
    )
    analyze_vegas_parser.add_argument(
        "--metrics",
        nargs="*",
        help="Lista de indicadores a analisar (padrão: todos)",
    )
    analyze_vegas_parser.set_defaults(func=run_analyze_vegas)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
