from typing import Annotated
from fastapi import Depends

from app.rules.loader import RulesLoader
from app.extraction.extractor import Extractor
from app.models.enums import Source
from app.models.models import InvalidRecordsData


class RequirementsValidator:

    def __init__(self, requirements_loader: RulesLoader, extractor: Extractor) -> None:
        self.loader = requirements_loader
        self.extractor = extractor

    def validate(self, source: Source, file_content: list) -> tuple[list, list[InvalidRecordsData]]:
        required_fields: list[str] = self.loader.load_requirements(source)

        validated = []
        invalid_records = []
        for index, record in enumerate(file_content, start=1):
            missing_fields = self._get_missing_fields(record, required_fields)
            if missing_fields:
                invalid_records.append(
                    InvalidRecordsData(
                        index=index,
                        content=record,
                        missing_fields=missing_fields
                    )
                )
                continue

            validated.append(record)
        
        return validated, invalid_records

    def _get_missing_fields(self, record: dict, requirements: list[str]) -> list[str]:
        missing_fields = []
        for field in requirements:
            if not self.extractor.extract(record, field):
                missing_fields.append(field)

        return missing_fields

def get_requirements_validator(
        requirements_loader: Annotated[RulesLoader, Depends()],
        extractor: Annotated[Extractor, Depends()]
) -> RequirementsValidator:
    return RequirementsValidator(
        requirements_loader=requirements_loader,
        extractor=extractor
    )