import requests, re
import base64
import os
import pandas as pd
from bs4 import BeautifulSoup
from config import DATA_RAW, DATA_PROCESSED

# ========== Spotify API ==========
def init_spotify_client():
    cid = os.getenv("SPOTIFY_CLIENT_ID")
    cs = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not cid or not cs:
        raise RuntimeError("Defina SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET.")

    auth_str = f"{cid}:{cs}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {b64_auth_str}"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(
        "https://accounts.spotify.com/api/token", headers=headers, data=data
    )
    return response.json()["access_token"]


def buscar_artista(nome, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/search?q={nome}&type=artist&limit=1"
    response = requests.get(url, headers=headers)
    return response.json()["artists"]["items"][0]


def buscar_top_musicas(artist_id, access_token, market="BR"):
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market={market}"
    response = requests.get(url, headers=headers)
    return response.json()["tracks"]


# ========== Last.fm API ==========
def buscar_dados_lastfm(artista_nome):
    api_key = os.getenv("LASTFM_API_KEY")
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getinfo",
        "artist": artista_nome,
        "api_key": api_key,
        "format": "json",
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return {"ouvintes_lastfm": None, "playcount_lastfm": None, "bio_resumo": ""}
    data = response.json().get("artist", {})
    return {
        "ouvintes_lastfm": int(data.get("stats", {}).get("listeners", 0)),
        "playcount_lastfm": int(data.get("stats", {}).get("playcount", 0)),
        "bio_resumo": data.get("bio", {})
        .get("summary", "")
        .split("<a href=")[0]
        .strip(),
    }


# ========== Kworb ==========
def buscar_kworb_streams(spotify_id):
    try:
        url = f"https://kworb.net/spotify/artist/{spotify_id}.html"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "lxml")
        tabela = soup.find("table", {"class": "sortable"})
        total_streams = 0
        if not tabela:
            return None
        for row in tabela.find_all("tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 5:
                try:
                    streams = int(cols[4].text.replace(",", ""))
                    total_streams += streams
                except Exception:
                    continue
        return {"kworb_total_streams": total_streams}
    except Exception:
        return None


# ========== Wikipedia fallback ==========
def buscar_wikipedia_sales(artista_nome):
    try:
        nome_formatado = artista_nome.replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{nome_formatado}_discography"
        response = requests.get(url)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, "lxml")
        texto = soup.get_text()
        match = re.search(
            r"has sold over ([\d,]+) (million|billion)? (records|albums)",
            texto,
            re.IGNORECASE,
        )
        if match:
            valor = match.group(1).replace(",", "")
            escala = match.group(2)
            numero = float(valor)
            if escala == "billion":
                numero *= 1_000_000_000
            elif escala == "million":
                numero *= 1_000_000
            return {"wikipedia_total_sales": int(numero)}
        return None
    except Exception:
        return None


def buscar_certificacoes_riaa(artista_nome):
    """
    Scraping da RIAA para coletar certificações e estimar vendas totais.
    """
    try:
        base_url = "https://www.riaa.com/gold-platinum/"
        search_url = f"{base_url}?tab_active=default-award&ar={artista_nome.replace(' ', '+')}#search_section"

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        tabela = soup.find("table", {"id": "search-award-table"})
        if not tabela:
            return None

        rows = tabela.find_all("tr", class_="table_award_row")

        total_vendas = 0
        maior_certificacao = ""
        certificacoes = []

        for row in rows:
            share_text = row.find("p", class_="share_text")
            if not share_text:
                continue
            descricao = share_text.get("data-share-desc", "").lower()

            # Ex: "earned RIAA 5x Platinum Award for DYNAMITE"
            match = re.search(
                r"(\d+)x?\s*(gold|platinum|multi-platinum|diamond)", descricao
            )
            if match:
                quantidade = int(match.group(1))
                tipo = match.group(2)

                if "diamond" in tipo:
                    vendas = quantidade * 10_000_000
                    nivel = "Diamond"
                elif "multi-platinum" in tipo or (
                    "platinum" in tipo and quantidade > 1
                ):
                    vendas = quantidade * 1_000_000
                    nivel = "Multi-Platinum"
                elif "platinum" in tipo:
                    vendas = 1_000_000
                    nivel = "Platinum"
                elif "gold" in tipo:
                    vendas = 500_000
                    nivel = "Gold"
                else:
                    vendas = 0
                    nivel = "Outro"

                total_vendas += vendas
                certificacoes.append((descricao, vendas))

                # Atualiza maior certificação
                ordem = ["Gold", "Platinum", "Multi-Platinum", "Diamond"]
                if ordem.index(nivel) > ordem.index(maior_certificacao or "Gold"):
                    maior_certificacao = nivel

        return {
            "riaa_vendas_estimadas": total_vendas,
            "riaa_maior_certificacao": maior_certificacao,
            "riaa_certificacoes": certificacoes,
        }

    except Exception as e:
        print(f"Erro ao buscar na RIAA: {e}")
        return None


# ========== Execução Principal ==========
def main():
    artistas = ["BTS", "BLACKPINK", "Lady Gaga"]
    access_token = init_spotify_client()
    dados_artistas = []

    for nome in artistas:
        try:
            artista = buscar_artista(nome, access_token)
            top_musicas = buscar_top_musicas(artista["id"], access_token)
            lastfm_info = buscar_dados_lastfm(artista["name"])
            kworb_info = buscar_kworb_streams(artista["id"])
            riaa_info = buscar_certificacoes_riaa(artista["name"])

            dados = {
                "nome": artista["name"],
                "popularidade_spotify": artista["popularity"],
                "seguidores_spotify": artista["followers"]["total"],
                "generos": ", ".join(artista["genres"]),
                "top_musicas": ", ".join([m["name"] for m in top_musicas]),
                "ouvintes_lastfm": lastfm_info["ouvintes_lastfm"],
                "playcount_lastfm": lastfm_info["playcount_lastfm"],
                "kworb_total_streams": (
                    kworb_info["kworb_total_streams"] if kworb_info else None
                ),
                "riaa_vendas_estimadas": (
                    riaa_info["riaa_vendas_estimadas"] if riaa_info else None
                ),
                "riaa_maior_certificacao": (
                    riaa_info["riaa_maior_certificacao"] if riaa_info else None
                ),
                "riaa_certificacoes": (
                    riaa_info["riaa_certificacoes"] if riaa_info else None
                ),
            }
            dados_artistas.append(dados)
        except Exception as e:
            print(f"Erro com artista {nome}: {e}")

    df = pd.DataFrame(dados_artistas)
    csv_path = DATA_PROCESSED / "dados_artistas.csv"
    df.to_csv(csv_path, index=False, sep=";")

if __name__ == "__main__":
    main()