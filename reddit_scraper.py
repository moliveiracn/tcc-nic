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
from config import (
    DATA_PROCESSED,
    FEMALE_TERMS,
    MALE_TERMS,
    DEMEAN_TERMS,
)

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


# ————— Correspondência de termos —————
def match_terms(text: str, hobby_regex: re.Pattern, insult_regex: re.Pattern) -> bool:
    """Retorna True se texto contiver ambos os padrões."""
    return hobby_regex.search(text) and insult_regex.search(text)


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
    hobby_query = re.sub(r"\W+", " ", hobby).strip()
    insult_query = re.sub(r"\W+", " ", insult).strip()
    query = (
        f'title:"{hobby_query}" AND title:"{insult_query}" '
        f'OR selftext:"{hobby_query}" AND selftext:"{insult_query}"'
    )
    submissions = reddit.subreddit("all").search(
        query, limit=posts_limit, syntax="lucene"
    )

    hobby_regex = re.compile(hobby, re.IGNORECASE)
    insult_regex = re.compile(insult, re.IGNORECASE)

    for sub in submissions:
        sub.comments.replace_more(limit=0)
        count = 0
        for c in sub.comments.list():
            if match_terms(c.body, hobby_regex, insult_regex):
                row = {
                    "pair": f"{hobby}|{insult}",
                    "post_id": sub.id,
                    "comment_id": c.id,
                    "subreddit": str(sub.subreddit),
                    "author": str(c.author),
                    "score": c.score,
                    "created_utc": datetime.utcfromtimestamp(c.created_utc).isoformat(),
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


def get_reddit_raw_data(post_limit=50, comment_limit=20):
    reddit = init_reddit_client()

    # Listas fixas de hobbies e termos depreciativos
    female = FEMALE_TERMS
    male = MALE_TERMS
    demean = DEMEAN_TERMS
    pairs = [(h, d) for h in (female + male) for d in demean]

    all_comments = []
    for hobby, insult in pairs:
        logging.info(f"🔎 Buscando comentários para: {hobby} + {insult}")
        try:
            rows = fetch_comments_for_pair(
                reddit,
                hobby,
                insult,
                posts_limit=post_limit,
                comments_limit=comment_limit,
            )
            all_comments.extend(rows)
        except Exception as e:
            logging.warning(f"Erro em {hobby}|{insult}: {e}")
        time.sleep(1)  # throttle entre pares

    logging.info(f"✅ Coleta de dados do Reddit concluída!")
    return all_comments


if __name__ == "__main__":
    # Exemplo de uso para teste, se necessário
    raw_data = get_reddit_raw_data(post_limit=10, comment_limit=5)
    df = pd.DataFrame(raw_data)
    csv_path = DATA_PROCESSED / "comments_raw_test.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"Dados brutos do Reddit salvos para teste em: {csv_path}")
