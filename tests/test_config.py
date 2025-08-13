import config
from pathlib import Path
import pytest


def test_data_paths_are_paths_and_directories_created():
    assert isinstance(config.DATA_RAW, Path)
    assert isinstance(config.DATA_PROCESSED, Path)
    assert isinstance(config.GRAPH_OUTPUT, Path)
    assert config.DATA_PROCESSED.is_dir()
    assert config.GRAPH_OUTPUT.is_dir()


@pytest.mark.parametrize(
    "name, terms",
    [
        ("FEMALE_TERMS", config.FEMALE_TERMS),
        ("MALE_TERMS", config.MALE_TERMS),
        ("DEMEAN_TERMS", config.DEMEAN_TERMS),
    ],
)
def test_term_lists_have_no_case_insensitive_duplicates(name, terms):
    lowered = [t.lower() for t in terms]
    assert len(lowered) == len(set(lowered)), f"Duplicate terms found in {name}"
