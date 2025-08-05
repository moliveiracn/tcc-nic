#!/usr/bin/env python3
"""
reddit_scraper.py

Busca comentários no Reddit que contenham pares de termos (hobby + insulto)
usando a API oficial (PRAW), enriquece os dados com métricas simples e
grava tudo num CSV de forma incremental.

Uso:
  export REDDIT_CID=...
  export REDDIT_CSECRET=...
  export REDDIT_USER_AGENT="tcc_nic_script/1.0"
  python reddit_scraper.py
    --post-limit 50 --comment-limit 20 --output comments.csv
"""

import os
import re
import csv
import time
import random
import logging
import argparse
from datetime import datetime
import praw
from config import DATA_PROCESSED

# ————— Configuração de logging —————
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


# ————— Helpers —————
def human_delay(min_s=1, max_s=3):
    """Pausa aleatória para simular comportamento humano."""
    time.sleep(random.uniform(min_s, max_s))


def enrich_row(row):
    """Adiciona métricas extras ao dicionário do comentário."""
    text = row["body"]
    row["word_count"] = len(text.split())
    row["char_count"] = len(text)
    row["hashtags"] = ",".join(re.findall(r"#\w+", text))
    row["mentions"] = ",".join(re.findall(r"@\w+", text))
    return row


# ————— Busca de comentários —————
def fetch_comments_for_pair(
    reddit, hobby, insult, posts_limit=50, comments_limit=20, sort="hot"
):
    """
    1) Busca submissions em r/all (ou subreddit especificado) cujo título
       ou corpo contenha hobby E insulto.
    2) Itera comentários desses posts, filtrando aqueles que contenham ambos.
    """
    rows = []
    query = (
        f'title:"{hobby}" AND title:"{insult}" '
        f'OR selftext:"{hobby}" AND selftext:"{insult}"'
    )
    submissions = reddit.subreddit("all").search(
        query, limit=posts_limit, syntax="lucene"
    )
    for sub in submissions:
        sub.comments.replace_more(limit=0)
        count = 0
        for c in sub.comments.list():
            body_low = c.body.lower()
            if hobby in body_low and insult in body_low:
                row = {
                    "pair": f"{hobby}|{insult}",
                    "post_id": sub.id,
                    "comment_id": c.id,
                    "subreddit": str(sub.subreddit),
                    "author": str(c.author),
                    "score": c.score,
                    "created_utc": datetime.fromtimestamp(c.created_utc),
                    "body": c.body.replace("\n", " "),
                }
                rows.append(enrich_row(row))
                count += 1
                if count >= comments_limit:
                    break
        logging.info(f"  → Encontrados {count} comentários em post {sub.id}")
        # human_delay()
    return rows


# ————— Escrita incremental em CSV —————
def write_comments_csv(filename, fieldnames, rows, first_write=False):
    mode = "w" if first_write else "a"
    with open(filename, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if first_write:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)


# ————— Argumentos de linha de comando —————
def parse_args():
    parser = argparse.ArgumentParser(
        description="Reddit scraper: hobby + insulto → comentários"
    )
    parser.add_argument(
        "--post-limit",
        type=int,
        default=50,
        help="Número máximo de posts para buscar (por par)",
    )
    parser.add_argument(
        "--comment-limit",
        type=int,
        default=20,
        help="Número máximo de comentários por post",
    )
    parser.add_argument(
        "--output",
        default=DATA_PROCESSED / "comments.csv",
        help="Arquivo CSV de saída",
    )
    return parser.parse_args()


# ————— Inicialização do cliente PRAW —————
def init_reddit_client():
    cid = os.getenv("REDDIT_CID")
    cs = os.getenv("REDDIT_CSECRET")
    ua = os.getenv("REDDIT_USER_AGENT")
    if not cid or not cs or not ua:
        raise RuntimeError("Defina REDDIT_CID, REDDIT_CSECRET e REDDIT_USER_AGENT.")
    return praw.Reddit(client_id=cid, client_secret=cs, user_agent=ua)


# ————— Fluxo principal —————
def main():
    args = parse_args()
    reddit = init_reddit_client()

    # Listas fixas de hobbies e termos depreciativos
    female = [
        "Honkai Star Rail",
        "Honkai: Star Rail",
        "HSR",
        "Infinity Nikki",
        "Genshin",
        "Genshin Impact",
        "WuWa",
        "Wuthering Waves",
        "love and deepspace",
        "Lady Gaga",  # specific interest
        "BTS",  # specific interest
        "Taylor Swift",  # specific interest
        "Ariana Grande",  # specific interest
        "Beyonce",  # specific interest
        "Kpop",  # genre with a large female fanbase
    ]
    male = []
    # male   = ["woodworking", "fishing", "gaming"]
    demean = [
        "basic",
        "cringe",
        "cringey",
        "silly",
        "frivolous",
        "superficial",
        "vain",
        "childish",
        "immature",
        "stupid",
        "dumb",
        "pointless",
        "useless",
        "waste of time",
        "not a real hobby",
        "trivial",
        "obsessed",  # in a negative connotation
        "fangirl",  # often used dismissively
        "crazy",  # when referring to fans
        "hysterical",
        "overly emotional",
        "dramatic",
        "airhead",
        "bimbo",
        "ditzy",
        "vapid",
        "shallow",
        "attention-seeking",
        "for girls",
        "that's for kids",
        "get a real interest",
        "unserious",
        "fluffy",
        "cute but dumb",
        "just a phase",
        "eye-roll",  # as an action/description
        "lame",
        "pathetic",
        "try-hard",
        "normie",  # can be used to mock mainstream feminine interests
        "soy",
        "simping",  # if the hobby involves devotion to a celebrity
        "delusional",  # for fans perceived as overly invested
    ]
    pairs = [(h, d) for h in (female + male) for d in demean]

    # Campos do CSV (incluindo colunas adicionadas pelo enrich_row)
    fieldnames = [
        "pair",
        "post_id",
        "comment_id",
        "subreddit",
        "author",
        "score",
        "created_utc",
        "body",
        "word_count",
        "char_count",
        "hashtags",
        "mentions",
    ]

    first = True
    for hobby, insult in pairs:
        logging.info(f"🔎 Buscando comentários para: {hobby} + {insult}")
        try:
            rows = fetch_comments_for_pair(
                reddit,
                hobby,
                insult,
                posts_limit=args.post_limit,
                comments_limit=args.comment_limit,
            )
            write_comments_csv(args.output, fieldnames, rows, first_write=first)
            first = False  # header apenas na primeira escrita
        except Exception as e:
            logging.warning(f"Erro em {hobby}|{insult}: {e}")
        time.sleep(1)  # throttle entre pares

    logging.info(f"✅ Concluído! Veja {args.output}")


if __name__ == "__main__":
    main()
