import pytest
from pathlib import Path
import pandas as pd
from unittest.mock import patch, MagicMock

from preprocess_data import main as preprocess_main
from config import DATA_PROCESSED, DATA_RAW

# Mock data for testing
@pytest.fixture
def mock_excel_files(tmp_path):
    # Create a dummy raw data directory
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy Excel files
    df_2021 = pd.DataFrame({
        "Metric": ["Visitors", "Average Room Rate"],
        "Jan": [100, 50],
        "Feb": [110, 55],
        "Mar": [120, 60],
        "Apr": [130, 65],
        "May": [140, 70],
        "Jun": [150, 75],
        "Jul": [160, 80],
        "Aug": [170, 85],
        "Sep": [180, 90],
        "Oct": [190, 95],
        "Nov": [200, 100],
        "Dec": [210, 105],
    })
    df_2021.to_excel(raw_dir / "Las Vegas 2021.xlsx", sheet_name="Las Vegas 2021", index=False)

    df_2022 = pd.DataFrame({
        "Metric": ["Visitors", "Average Room Rate"],
        "Jan": [220, 110],
        "Feb": [230, 115],
        "Mar": [240, 120],
        "Apr": [250, 125],
        "May": [260, 130],
        "Jun": [270, 135],
        "Jul": [280, 140],
        "Aug": [290, 145],
        "Sep": [300, 150],
        "Oct": [310, 155],
        "Nov": [320, 160],
        "Dec": [330, 165],
    })
    df_2022.to_excel(raw_dir / "Las Vegas 2022.xlsx", sheet_name="Las Vegas 2022", index=False)

    return raw_dir

@pytest.fixture
def mock_processed_dir(tmp_path):
    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    return processed_dir

def test_preprocess_main_excel_processing(mock_excel_files, mock_processed_dir, monkeypatch):
    monkeypatch.setattr("config.DATA_RAW", mock_excel_files)
    monkeypatch.setattr("config.DATA_PROCESSED", mock_processed_dir)

    preprocess_main()

    output_file = mock_processed_dir / "vegas_tourism_yearly.csv"
    assert output_file.exists()

    df_processed = pd.read_csv(output_file, index_col='Date', parse_dates=True)
    assert not df_processed.empty
    assert "Visitors" in df_processed.columns
    assert "Average Room Rate" in df_processed.columns
    assert len(df_processed['Year'].unique()) == 2

@patch('artists_info.get_artist_raw_data')
def test_preprocess_main_artists_processing(mock_get_artist_raw_data, mock_excel_files, mock_processed_dir, monkeypatch):
    monkeypatch.setattr("config.DATA_RAW", mock_excel_files)
    monkeypatch.setattr("config.DATA_PROCESSED", mock_processed_dir)

    mock_get_artist_raw_data.return_value = [
        {"nome": "Artist1", "popularidade_spotify": 80},
        {"nome": "Artist2", "popularidade_spotify": 70},
    ]

    preprocess_main()

    output_file = mock_processed_dir / "artists_processed.csv"
    assert output_file.exists()
    df_artists = pd.read_csv(output_file, sep=";")
    assert not df_artists.empty
    assert "Artist1" in df_artists["nome"].values
    mock_get_artist_raw_data.assert_called_once()

@patch('flights_parser.get_flight_raw_data')
def test_preprocess_main_flights_processing(mock_get_flight_raw_data, mock_excel_files, mock_processed_dir, monkeypatch):
    monkeypatch.setattr("config.DATA_RAW", mock_excel_files)
    monkeypatch.setattr("config.DATA_PROCESSED", mock_processed_dir)

    mock_get_flight_raw_data.return_value = [
        ["Ticket1", "CarrierA", "202203", "C1", "S1", "OriginA", "WACA", "R", "F1", 1, "MktA", "OpA", 100.0, "LAS", 1000.0],
        ["Ticket2", "CarrierB", "202203", "C2", "S2", "OriginB", "WACB", "R", "F2", 1, "MktB", "OpB", 200.0, "LAS", 2000.0],
    ]
    monkeypatch.setattr('flights_parser.HEADER', [
        "TicketID", "UniqueCarrier", "YearQuarter", "CouponNum", "SequenceNum",
        "Origin", "OriginWAC", "Roundtrip", "FareClass", "SegmentNum",
        "MarketingCarrier", "OperatingCarrier", "Distance", "ArrivalAirport", "FareAmount"
    ])

    preprocess_main()

    output_file = mock_processed_dir / "flights_processed.csv"
    assert output_file.exists()
    df_flights = pd.read_csv(output_file, sep=";")
    assert not df_flights.empty
    assert "Ticket1" in df_flights["TicketID"].values
    mock_get_flight_raw_data.assert_called_once()

@patch('reddit_scraper.get_reddit_raw_data')
def test_preprocess_main_reddit_processing(mock_get_reddit_raw_data, mock_excel_files, mock_processed_dir, monkeypatch):
    monkeypatch.setattr("config.DATA_RAW", mock_excel_files)
    monkeypatch.setattr("config.DATA_PROCESSED", mock_processed_dir)

    mock_get_reddit_raw_data.return_value = [
        {"pair": "hobby|insult", "body": "comment 1", "word_count": 2},
        {"pair": "hobby|insult", "body": "comment 2", "word_count": 2},
    ]

    preprocess_main()

    output_file = mock_processed_dir / "reddit_processed.csv"
    assert output_file.exists()
    df_reddit = pd.read_csv(output_file, sep=";")
    assert not df_reddit.empty
    assert "comment 1" in df_reddit["body"].values
    mock_get_reddit_raw_data.assert_called_once()
