import pytest
from pathlib import Path
from flights_parser import get_flight_raw_data, process_file, HEADER

@pytest.fixture
def mock_raw_flight_files(tmp_path):
    # Create a dummy raw data directory
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy .asc files
    file1_content = """
Ticket1|CarrierA|202203|C1|S1|OriginA|WACA|R|F1|Seg1|MktA|OpA|100|DestA|1000|Seg2|MktB|OpB|200|LAS|2000
Ticket2|CarrierB|202203|C2|S2|OriginB|WACB|R|F2|Seg1|MktC|OpC|300|LAS|3000
"""
    file2_content = """
Ticket3|CarrierC|202204|C3|S3|OriginC|WACC|R|F3|Seg1|MktD|OpD|400|LAS|4000
"""
    (raw_dir / "db1b.public.202203.asc").write_text(file1_content)
    (raw_dir / "db1b.public.202204.asc").write_text(file2_content)

    return raw_dir

def test_process_file(mock_raw_flight_files):
    file_path = mock_raw_flight_files / "db1b.public.202203.asc"
    rows = process_file(file_path)

    assert len(rows) == 2
    assert rows[0][0] == "Ticket1"
    assert rows[0][13] == "LAS"
    assert rows[0][14] == 2000.0
    assert rows[1][0] == "Ticket2"
    assert rows[1][13] == "LAS"
    assert rows[1][14] == 3000.0

def test_get_flight_raw_data(mock_raw_flight_files, monkeypatch):
    monkeypatch.setattr("config.DATA_RAW", mock_raw_flight_files)

    raw_data = get_flight_raw_data()

    assert len(raw_data) == 3  # 2 from first file, 1 from second
    assert raw_data[0][0] == "Ticket1"
    assert raw_data[2][0] == "Ticket3"

    # Ensure the header is not included in the raw data
    assert raw_data[0] != HEADER
