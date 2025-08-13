import sys
import types
from unittest.mock import MagicMock
import pytest

import run


def test_artists_subcommand_invokes_main(monkeypatch):
    stub = types.ModuleType("artists_info")
    stub.main = MagicMock()
    monkeypatch.setitem(sys.modules, "artists_info", stub)
    monkeypatch.setattr(sys, "argv", ["run.py", "artists"])
    run.main()
    stub.main.assert_called_once_with()


def test_flights_subcommand_invokes_process(monkeypatch):
    stub = types.ModuleType("flights_parser")
    stub.process_all_files = MagicMock()
    monkeypatch.setitem(sys.modules, "flights_parser", stub)
    monkeypatch.setattr(sys, "argv", ["run.py", "flights"])
    run.main()
    stub.process_all_files.assert_called_once_with()


def test_reddit_subcommand_passes_args(monkeypatch):
    stub = types.ModuleType("reddit_scraper")
    stub.main = MagicMock()
    monkeypatch.setitem(sys.modules, "reddit_scraper", stub)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run.py",
            "reddit",
            "--post-limit",
            "10",
            "--comment-limit",
            "5",
            "--output",
            "out.csv",
        ],
    )
    run.main()
    stub.main.assert_called_once_with(post_limit=10, comment_limit=5, output="out.csv")


def test_preprocess_subcommand_invokes_main(monkeypatch):
    stub = types.ModuleType("preprocess_vegas_data")
    stub.main = MagicMock()
    monkeypatch.setitem(sys.modules, "preprocess_vegas_data", stub)
    monkeypatch.setattr(sys, "argv", ["run.py", "preprocess"])
    run.main()
    stub.main.assert_called_once_with()


def test_excel_subcommand_passes_metrics(monkeypatch):
    stub = types.ModuleType("analyze_excel")
    stub.main = MagicMock()
    monkeypatch.setitem(sys.modules, "analyze_excel", stub)
    monkeypatch.setattr(
        sys,
        "argv",
        ["run.py", "excel", "--metrics", "Visitors", "Revenue"],
    )
    run.main()
    stub.main.assert_called_once_with(metrics=["Visitors", "Revenue"])


def test_unknown_subcommand_raises_system_exit(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["run.py", "unknown"])
    with pytest.raises(SystemExit) as err:
        run.main()
    assert err.value.code == 2
