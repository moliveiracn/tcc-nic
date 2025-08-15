import pytest
import requests
from artists_info import (
    init_spotify_client,
    buscar_dados_lastfm,
    buscar_kworb_streams,
    buscar_wikipedia_sales,
)


def test_init_spotify_client(monkeypatch):
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "cid")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "secret")

    def fake_post(url, headers=None, data=None):
        class Resp:
            def json(self):
                return {"access_token": "token"}

        return Resp()

    monkeypatch.setattr(requests, "post", fake_post)
    token = init_spotify_client()
    assert token == "token"


def test_buscar_dados_lastfm_valid(monkeypatch):
    monkeypatch.setenv("LASTFM_API_KEY", "abc")

    def fake_get(url, params=None):
        class Resp:
            status_code = 200

            def json(self):
                return {
                    "artist": {
                        "stats": {"listeners": "100", "playcount": "200"},
                        "bio": {"summary": "Bio text <a href='url'>more</a>"},
                    }
                }

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    data = buscar_dados_lastfm("Artist")
    assert data == {
        "ouvintes_lastfm": 100,
        "playcount_lastfm": 200,
        "bio_resumo": "Bio text",
    }


def test_buscar_dados_lastfm_non_200(monkeypatch):
    monkeypatch.setenv("LASTFM_API_KEY", "abc")

    def fake_get(url, params=None):
        class Resp:
            status_code = 404

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    data = buscar_dados_lastfm("Artist")
    assert data == {
        "ouvintes_lastfm": None,
        "playcount_lastfm": None,
        "bio_resumo": "",
    }


def test_buscar_dados_lastfm_malformed_json(monkeypatch):
    monkeypatch.setenv("LASTFM_API_KEY", "abc")

    def fake_get(url, params=None):
        class Resp:
            status_code = 200

            def json(self):
                raise ValueError("bad json")

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    with pytest.raises(ValueError):
        buscar_dados_lastfm("Artist")


def test_buscar_kworb_streams(monkeypatch):
    html = """
    <html><body>
    <table class='sortable'>
        <tr><th></th></tr>
        <tr><td></td><td></td><td></td><td></td><td>1,000</td></tr>
        <tr><td></td><td></td><td></td><td></td><td>2,000</td></tr>
    </table>
    </body></html>
    """

    def fake_get(url):
        class Resp:
            status_code = 200
            text = html

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    result = buscar_kworb_streams("id")
    assert result == {"kworb_total_streams": 3000}


def test_buscar_wikipedia_sales_match(monkeypatch):
    html = "The artist has sold over 10 million albums worldwide."

    def fake_get(url):
        class Resp:
            status_code = 200
            text = html

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    result = buscar_wikipedia_sales("Artist")
    assert result == {"wikipedia_total_sales": 10_000_000}


def test_buscar_wikipedia_sales_no_match(monkeypatch):
    html = "No sales info here."

    def fake_get(url):
        class Resp:
            status_code = 200
            text = html

        return Resp()

    monkeypatch.setattr(requests, "get", fake_get)
    assert buscar_wikipedia_sales("Artist") is None
