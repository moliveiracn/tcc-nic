import sys
import types
from unittest.mock import MagicMock
import pytest

import run


def test_preprocess_subcommand_invokes_main(monkeypatch):
    stub = types.ModuleType("preprocess_data")
    stub.main = MagicMock()
    monkeypatch.setitem(sys.modules, "preprocess_data", stub)
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
