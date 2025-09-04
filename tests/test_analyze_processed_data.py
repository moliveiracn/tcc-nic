import pandas as pd
import pytest
from unittest.mock import patch
 
from analyze_processed_data import (
    load_data,
    plot_yearly_comparison,
    comparative_analysis,
    main,
)

@pytest.fixture
def sample_df():
    """Pytest fixture providing a sample DataFrame for testing."""
    dates = pd.to_datetime(
        [
            "2021-03-01",
            "2021-04-01",
            "2021-05-01",
            "2022-03-01",
            "2022-04-01",
            "2022-05-01",
            "2023-04-01",
        ]
    )
    data = {
        "Visitors": [100, 110, 120, 130, 200, 140, 150],
        "Revenue": [1000, 1100, 1200, 1300, 2500, 1400, 1500],
        "Year": [2021, 2021, 2021, 2022, 2022, 2022, 2023],
        "Month": [3, 4, 5, 3, 4, 5, 4],
    }
    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"
    return df


def test_load_data_success(monkeypatch, tmp_path, sample_df):
    """Tests that data is loaded correctly from a CSV file."""
    file_path = tmp_path / "test_data.csv"
    sample_df.to_csv(file_path)

    monkeypatch.setattr("analyze_processed_data.PROCESSED_DATA_FILE", file_path)

    loaded_df = load_data()
    assert isinstance(loaded_df, pd.DataFrame)
    # parse_dates in read_csv can affect index type, so we compare values
    pd.testing.assert_frame_equal(loaded_df, sample_df)

def test_load_data_file_not_found(monkeypatch, capsys):
    """Tests that it handles a missing file gracefully."""
    monkeypatch.setattr("analyze_processed_data.PROCESSED_DATA_FILE", "non_existent.csv")

    result = load_data()
    assert result is None
    captured = capsys.readouterr()
    assert "Erro: Arquivo de dados processado não encontrado" in captured.out


@patch("analyze_processed_data.plt")
def test_plot_yearly_comparison(mock_plt, tmp_path, monkeypatch, sample_df):
    """Tests that the plotting function calls matplotlib correctly."""
    monkeypatch.setattr("analyze_processed_data.GRAPH_OUTPUT", tmp_path)
    plot_yearly_comparison(sample_df, "Visitors", "Test Title", "Test YLabel")

    mock_plt.figure.assert_called_once()
    mock_plt.title.assert_called_with("Test Title", fontsize=16)
    mock_plt.ylabel.assert_called_with("Test YLabel")

    # Check that the event highlight was plotted
    mock_plt.scatter.assert_called_once()
    args, kwargs = mock_plt.scatter.call_args
    assert args[0] == 4  # EVENT_MONTH
    assert args[1] == 200  # Value for Visitors in April 2022
    assert kwargs["label"] == "Shows BTS (2022)"

    expected_path = tmp_path / "comparison_visitors.png"
    mock_plt.savefig.assert_called_with(expected_path)
    mock_plt.close.assert_called_once()

def test_comparative_analysis_prints_correctly(capsys, sample_df):
    """Tests the quantitative analysis output."""
    comparative_analysis(sample_df, ["Visitors", "Revenue"])

    captured = capsys.readouterr()
    output = captured.out

    assert "Análise de Impacto Quantitativo: Shows BTS (Abril de 2022)" in output
    assert "Valor em Abr/2022: 200.00" in output
    assert "Média de Abril (outros anos): 130.00" in output  # (110+150)/2
    assert "Impacto vs. outros Abrils: +53.85%" in output


def test_comparative_analysis_no_event_data(capsys, sample_df):
    """Tests the warning message when event data is missing."""
    df_no_event = sample_df[sample_df.index.year != 2022]  # Remove event year

    comparative_analysis(df_no_event, ["Visitors"])

    captured = capsys.readouterr()
    assert "Aviso: não há dados para 04/2022" in captured.out


@patch("analyze_processed_data.load_data")
@patch("analyze_processed_data.plot_yearly_comparison")
@patch("analyze_processed_data.comparative_analysis")
def test_main_full_run(mock_analysis, mock_plot, mock_load, sample_df):
    """Tests the main function orchestrates calls correctly."""
    mock_load.return_value = sample_df

    main()

    mock_load.assert_called_once()
    assert mock_plot.call_count == 2  # For 'Visitors' and 'Revenue'
    mock_analysis.assert_called_once_with(sample_df, ["Visitors", "Revenue"])


@patch("analyze_processed_data.load_data")
def test_main_with_missing_metric(mock_load, capsys, sample_df):
    """Tests that a warning is printed for metrics that don't exist."""
    mock_load.return_value = sample_df

    main(metrics=["Visitors", "NonExistentMetric"])

    captured = capsys.readouterr()
    assert "Aviso: Indicadores não encontrados: NonExistentMetric" in captured.out


@patch("analyze_processed_data.load_data")
@patch("analyze_processed_data.comparative_analysis")
def test_main_with_no_metrics(mock_analysis, mock_load, sample_df):
    """Tests that calling main with no metrics analyzes all available ones."""
    mock_load.return_value = sample_df

    main(metrics=None)  # Explicitly pass None

    mock_load.assert_called_once()
    # Should be called with all available metrics from the sample_df
    mock_analysis.assert_called_once_with(sample_df, ["Visitors", "Revenue"])
