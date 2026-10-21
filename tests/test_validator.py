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

    validated, invalid = validator.validate(Source.CUSTOM, [record])

    assert validated == [record]
    assert invalid == []


def test_missing_required_field_fails(validator):
    record = {
        "title": "Dora Arch",
        "digital_file": {
            "file_url": "http://example.com/model.obj"
        }
    }

    validated, invalid = validator.validate(Source.CUSTOM, [record])

    assert validated == []
    assert len(invalid) == 1
    assert invalid[0].missing_fields == ["creator"]


def test_empty_value_fails(validator):
    record = {
        "title": "",
        "creator": "Anonymous",
        "digital_file": {
            "file_url": "http://example.com/model.obj"
        }
    }

    validated, invalid = validator.validate(Source.CUSTOM, [record])

    assert validated == []
    assert len(invalid) == 1
    assert invalid[0].missing_fields == ["title"]


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


def test_invalid_record_index_is_one_based(validator):
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
            "creator": "Museum"
        }
    ]

    validated, invalid = validator.validate(Source.CUSTOM, records)

    assert validated == records[:1]
    assert len(invalid) == 1
    assert invalid[0].index == 2
    assert invalid[0].missing_fields == ["digital_file.file_url"]


def test_validate_returns_invalid_record_details(validator):
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

    validated, invalid = validator.validate(Source.CUSTOM, records)

    assert validated == records[:1]
    assert len(invalid) == 1
    assert invalid[0].index == 2
    assert invalid[0].content == records[1]
    assert invalid[0].missing_fields == ["creator", "digital_file.file_url"]