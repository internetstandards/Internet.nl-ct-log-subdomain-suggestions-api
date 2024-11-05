import pytest
import pathlib

@pytest.fixture
def testdata():
    return pathlib.Path(__file__).parent / "testdata"
