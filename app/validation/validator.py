from typing import Annotated
from fastapi import Depends

from app.rules.loader import RulesLoader
from app.extraction.extractor import Extractor
from app.models.enums import Source


class RequirementsValidator:

    def __init__(self, requirements_loader: RulesLoader, extractor: Extractor) -> None:
        self.loader = requirements_loader
        self.extractor = extractor

    def validate(self, source: Source, file_content: list) -> list:
        required_fields: list[str] = self.loader.load_requirements(source)

        validated = []
        for record in file_content:
            if not self._is_record_valid(record, required_fields):
                continue

            validated.append(record)
        
        return validated

    def _is_record_valid(self, record: dict, requirements: list[str]) -> bool:
        for field in requirements:
            if not self.extractor.extract(record, field):
                return False

        return True

def get_requirements_validator(
        requirements_loader: Annotated[RulesLoader, Depends()],
        extractor: Annotated[Extractor, Depends()]
) -> RequirementsValidator:
    return RequirementsValidator(
        requirements_loader=requirements_loader,
        extractor=extractor
    )