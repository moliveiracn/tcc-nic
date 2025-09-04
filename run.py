import argparse
from config import DATA_PROCESSED


def run_preprocess(args):
    print("▶️ Executando o módulo 'preprocess_data'...")
    from preprocess_data import main as preprocess_main
    preprocess_main()


def run_analyze_processed_data(args):
    print("▶️ Executando o módulo 'analyze_processed_data'...")
    from analyze_processed_data import main as analyze_main
    analyze_main(metrics=args.metrics)


def main():
    """Ponto de entrada principal para executar os diferentes módulos do projeto.

    Uso:
        python run.py <modulo> [opções]

    Exemplos:
        python run.py preprocess
        python run.py excel --metrics Visitors
    """
    parser = argparse.ArgumentParser(
        description="Orquestrador de scripts do projeto TCC.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="module", required=True)

    preprocess_parser = subparsers.add_parser(
        "preprocess", help="Padroniza dados."
    )
    preprocess_parser.set_defaults(func=run_preprocess)

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analisa dados de turismo de Las Vegas e gera gráficos.",
    )
    analyze_parser.add_argument(
        "--metrics",
        nargs="*",
        help="Lista de indicadores a analisar (padrão: todos)",
    )
    analyze_parser.set_defaults(func=run_analyze_processed_data)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
