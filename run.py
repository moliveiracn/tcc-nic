import argparse
import sys

def main():
    """
    Ponto de entrada principal para executar os diferentes módulos do projeto.
    Use:
        python run.py --module <nome_do_modulo>
    Exemplos:
        python run.py --module artists
        python run.py --module flights
        python run.py --module reddit --post-limit 10
        python run.py --module preprocess
        python run.py --module excel
    """
    parser = argparse.ArgumentParser(
        description="Orquestrador de scripts do projeto TCC.",
        formatter_class=argparse.RawTextHelpFormatter # Melhora a formatação da ajuda
    )
    
    parser.add_argument(
        "--module",
        "-m",
        required=True,
        choices=["artists", "flights", "reddit", "preprocess", "excel"],
        help=(
            "Nome do módulo a ser executado:\n"
            "  - artists: Coleta dados de artistas (Spotify, Last.fm, etc.).\n"
            "  - flights: Processa dados brutos de voos para Las Vegas.\n"
            "  - reddit:  Busca comentários no Reddit (aceita args extras).\n"
            "  - preprocess:  Padroniza dados.\n"
            "  - excel:   Analisa dados de turismo de Las Vegas e gera gráficos."
        )
    )
    
    # Captura o argumento --module antes de passar os restantes
    args, remaining_args = parser.parse_known_args()
    
    if args.module == "artists":
        print("▶️ Executando o módulo 'artists_info'...")
        from artists_info import main as artists_main
        artists_main() # Supõe que a lógica principal de artists_info.py está em uma função main()
        
    elif args.module == "flights":
        print("▶️ Executando o módulo 'flights_parser'...")
        from flights_parser import process_all_files
        process_all_files()
        
    elif args.module == "reddit":
        print("▶️ Executando o módulo 'reddit_scraper'...")
        # Adicionamos os argumentos do reddit_scraper aqui
        # para que 'python run.py --module reddit --help' funcione
        from reddit_scraper import main as reddit_main
        sys.argv = [sys.argv[0]] + remaining_args # Passa os argumentos restantes para o scraper
        reddit_main()
        
    elif args.module == "preprocess":
        print("▶️ Executando o módulo 'preprocess_vegas_data'...")
        from preprocess_vegas_data import main as preprocess_main
        preprocess_main()

    elif args.module == "excel":
        print("▶️ Executando o módulo 'analyze_excel'...")
        from analyze_excel import main as excel_main
        excel_main()

if __name__ == "__main__":
    main()