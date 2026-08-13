import pytest

from app.validation.validator import RequirementsValidator
from app.models.enums import Source


class DummyRequirementsLoader:
    def __init__(self, requirements):
        self.requirements = requirements

    def load_requirements(self, source):
        return self.requirements


class DummyExtractor:
    def extract(self, record, path):
        parts = path.split(".")

        value = record
        for part in parts:
            if part not in value:
                return None
            value = value[part]

        return value


@pytest.fixture
def validator():
    return RequirementsValidator(
        requirements_loader=DummyRequirementsLoader(
            [
                "title",
                "creator",
                "digital_file.file_url"
            ]
        ),
        extractor=DummyExtractor()
    )


def test_valid_record_passes(validator):
    record = {
        "title": "Dora Arch",
        "creator": "Anonymous",
        "digital_file": {
            "file_url": "http://example.com/model.obj"
        }
    }

    assert validator.is_record_valid(
        record,
        ["title", "creator", "digital_file.file_url"]
    )


def test_missing_required_field_fails(validator):
    record = {
        "title": "Dora Arch",
        "digital_file": {
            "file_url": "http://example.com/model.obj"
        }
    }

    assert not validator.is_record_valid(
        record,
        ["title", "creator", "digital_file.file_url"]
    )


def test_empty_value_fails(validator):
    record = {
        "title": "",
        "creator": "Anonymous",
        "digital_file": {
            "file_url": "http://example.com/model.obj"
        }
    }

    assert not validator.is_record_valid(
        record,
        ["title", "creator", "digital_file.file_url"]
    )


def test_validate_accepts_all_records(validator):
    records = [
        {
            "title": "Object 1",
            "creator": "Museum",
            "digital_file": {
                "file_url": "http://example.com/1.obj"
            }
        },
        {
            "title": "Object 2",
            "creator": "Museum",
            "digital_file": {
                "file_url": "http://example.com/2.obj"
            }
        }
    ]

    validator.validate(Source.CUSTOM, records)


def test_validate_raises_error_for_invalid_record(validator):
    records = [
        {
            "title": "Object 1",
            "creator": "Museum",
            "digital_file": {
                "file_url": "http://example.com/1.obj"
            }
        },
        {
            "title": "Object 2"
        }
    ]

    with pytest.raises(ValueError, match="Invalid record"):
        validator.validate(Source.CUSTOM, records)