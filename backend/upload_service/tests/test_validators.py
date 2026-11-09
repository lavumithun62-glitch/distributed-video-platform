import pytest

from fastapi import HTTPException

from backend.upload_service.app.validators import (
    validate_extension,
    validate_file_size,
)


def test_valid_mp4_extension():
    assert validate_extension("sample.mp4") == ".mp4"


def test_valid_mkv_extension():
    assert validate_extension("sample.mkv") == ".mkv"


def test_invalid_extension():
    with pytest.raises(HTTPException) as error:
        validate_extension("sample.exe")

    assert error.value.status_code == 415


def test_valid_file_size():
    validate_file_size(1024)


def test_empty_file():
    with pytest.raises(HTTPException) as error:
        validate_file_size(0)

    assert error.value.status_code == 400


def test_oversized_file():
    with pytest.raises(HTTPException) as error:
        validate_file_size(600 * 1024 * 1024)

    assert error.value.status_code == 413