import argparse
from config import DATA_PROCESSED


def run_artists(args):
    print("▶️ Executando o módulo 'artists_info'...")
    from artists_info import main as artists_main
    artists_main()


def run_flights(args):
    print("▶️ Executando o módulo 'flights_parser'...")
    from flights_parser import process_all_files
    process_all_files()


def run_reddit(args):
    print("▶️ Executando o módulo 'reddit_scraper'...")
    from reddit_scraper import main as reddit_main
    reddit_main(
        post_limit=args.post_limit,
        comment_limit=args.comment_limit,
        output=args.output,
    )


def run_preprocess(args):
    print("▶️ Executando o módulo 'preprocess_vegas_data'...")
    from preprocess_vegas_data import main as preprocess_main
    preprocess_main()


def run_excel(args):
    print("▶️ Executando o módulo 'analyze_excel'...")
    from analyze_excel import main as excel_main
    excel_main(metrics=args.metrics)


def main():
    """Ponto de entrada principal para executar os diferentes módulos do projeto.

    Uso:
        python run.py <modulo> [opções]

    Exemplos:
        python run.py artists
        python run.py flights
        python run.py reddit --post-limit 10
        python run.py preprocess
        python run.py excel --metrics Visitors
    """
    parser = argparse.ArgumentParser(
        description="Orquestrador de scripts do projeto TCC.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="module", required=True)

    artists_parser = subparsers.add_parser(
        "artists", help="Coleta dados de artistas (Spotify, Last.fm, etc.)"
    )
    artists_parser.set_defaults(func=run_artists)

    flights_parser = subparsers.add_parser(
        "flights", help="Processa dados brutos de voos para Las Vegas."
    )
    flights_parser.set_defaults(func=run_flights)

    reddit_parser = subparsers.add_parser(
        "reddit", help="Busca comentários no Reddit (aceita args extras)."
    )
    reddit_parser.add_argument(
        "--post-limit",
        type=int,
        default=50,
        help="Número máximo de posts para buscar (por par)",
    )
    reddit_parser.add_argument(
        "--comment-limit",
        type=int,
        default=20,
        help="Número máximo de comentários por post",
    )
    reddit_parser.add_argument(
        "--output",
        default=DATA_PROCESSED / "comments.csv",
        help="Arquivo CSV de saída",
    )
    reddit_parser.set_defaults(func=run_reddit)

    preprocess_parser = subparsers.add_parser(
        "preprocess", help="Padroniza dados."
    )
    preprocess_parser.set_defaults(func=run_preprocess)

    excel_parser = subparsers.add_parser(
        "excel",
        help="Analisa dados de turismo de Las Vegas e gera gráficos.",
    )
    excel_parser.add_argument(
        "--metrics",
        nargs="*",
        help="Lista de indicadores a analisar (padrão: todos)",
    )
    excel_parser.set_defaults(func=run_excel)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
