import re
from unittest.mock import MagicMock

import pytest

from reddit_scraper import (
    enrich_row,
    match_terms,
    write_comments_csv,
    init_reddit_client,
)


def test_enrich_row_counts_hashtags_mentions():
    row = {"body": "Hello world #tag1 #tag2 @user1 @user2"}
    enriched = enrich_row(row.copy())
    assert enriched["word_count"] == 6
    assert enriched["char_count"] == len(row["body"])
    assert enriched["hashtags"] == "#tag1,#tag2"
    assert enriched["mentions"] == "@user1,@user2"


def test_match_terms_with_mocked_patterns():
    hobby = MagicMock()
    insult = MagicMock()
    hobby.search.return_value = True
    insult.search.return_value = True
    assert match_terms("sample text", hobby, insult)
    insult.search.return_value = None
    assert not match_terms("sample text", hobby, insult)
    hobby.search.assert_called_with("sample text")
    insult.search.assert_called_with("sample text")


def test_write_comments_csv_appends_without_dup_headers(tmp_path):
    file = tmp_path / "comments.csv"
    fieldnames = ["a", "b"]
    rows1 = [{"a": "1", "b": "2"}]
    write_comments_csv(file, fieldnames, rows1, first_write=True)
    rows2 = [{"a": "3", "b": "4"}]
    write_comments_csv(file, fieldnames, rows2, first_write=False)
    lines = file.read_text().splitlines()
    assert lines[0] == "a,b"
    assert lines[1:] == ["1,2", "3,4"]


def test_init_reddit_client_success(monkeypatch):
    monkeypatch.setenv("REDDIT_CID", "cid")
    monkeypatch.setenv("REDDIT_CSECRET", "secret")
    monkeypatch.setenv("REDDIT_USER_AGENT", "ua")
    fake = MagicMock(return_value="client")
    import praw

    monkeypatch.setattr(praw, "Reddit", fake)
    client = init_reddit_client()
    assert client == "client"
    fake.assert_called_once_with(client_id="cid", client_secret="secret", user_agent="ua")


def test_init_reddit_client_missing_env(monkeypatch):
    monkeypatch.delenv("REDDIT_CID", raising=False)
    monkeypatch.delenv("REDDIT_CSECRET", raising=False)
    monkeypatch.delenv("REDDIT_USER_AGENT", raising=False)
    with pytest.raises(RuntimeError):
        init_reddit_client()
