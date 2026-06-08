from pathlib import Path

_current_folder = Path(__file__).parent
_FILENAME_EVE_SDE_TESTDATA = "eve_sde.json"


def test_data_filename():
    return str(_current_folder / _FILENAME_EVE_SDE_TESTDATA)


def test_image_filename():
    return str(_current_folder / "test_image.jpg")
