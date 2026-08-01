import pytest

from app.extraction.extractor import Extractor


@pytest.fixture
def extractor():
    return Extractor()


@pytest.fixture
def record():
    return {
        "id": "123",
        "title": "Object title",
        "creator": {
            "name": "John Doe"
        },
        "metadata": {
            "dates": [
                {
                    "type": "creation",
                    "value": "1650"
                },
                {
                    "type": "publication",
                    "value": "1700"
                }
            ]
        },
        "proxies": [
            {
                "dcTitle": {
                    "en": [
                        "English title"
                    ]
                }
            },
            {
                "dcTitle": {
                    "en": [
                        "Second title"
                    ]
                }
            }
        ]
    }


def test_extract_simple_field(extractor, record):
    result = extractor.extract(record, "id")

    assert result == "123"


def test_extract_nested_field(extractor, record):
    result = extractor.extract(record, "creator.name")

    assert result == "John Doe"


def test_extract_missing_field(extractor, record):
    result = extractor.extract(record, "creator.lastname")

    assert result is None


def test_extract_list_field(extractor, record):
    result = extractor.extract(record, "metadata.dates[]")

    assert result == [
        {
            "type": "creation",
            "value": "1650"
        },
        {
            "type": "publication",
            "value": "1700"
        }
    ]


def test_extract_field_inside_list(extractor, record):
    result = extractor.extract(record, "metadata.dates[].value")

    assert result == [
        "1650",
        "1700"
    ]


def test_extract_nested_list_field(extractor, record):
    result = extractor.extract(record, "proxies[].dcTitle.en[]")

    assert result == [
        [
            "English title"
        ],
        [
            "Second title"
        ]
    ]


def test_extract_list_from_non_list(extractor, record):
    result = extractor.extract(record, "id[]")

    assert result is None


def test_extract_from_non_dict(extractor, record):
    result = extractor.extract(record, "title.value")

    assert result is None


def test_extract_empty_path(extractor, record):
    result = extractor.extract(record, "")

    assert result is None