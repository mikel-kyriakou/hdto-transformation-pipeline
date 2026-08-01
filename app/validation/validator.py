from typing import Annotated
from fastapi import Depends

from app.validation.loader import RequirementsLoader
from app.extraction.extractor import Extractor
from app.models.enums import Source


class RequirementsValidator:

    def __init__(self, requirements_loader: RequirementsLoader, extractor: Extractor) -> None:
        self.loader = requirements_loader
        self.extractor = extractor

    def validate(self, source: Source, file_content: list) -> None:
        required_fields: list[str] = self.loader.load(source)

        for record in file_content:
            if not self.is_record_valid(record, required_fields):
                #TODO change exception to include more data (e.g. record failed, missing field)
                raise ValueError("Invalid record")
        
        return

    def is_record_valid(self, record: dict, requirements: list[str]) -> bool:
        for field in requirements:
            if not self.extractor.extract(record, field):
                return False

        return True

def get_requirements_validator(
        requirements_loader: Annotated[RequirementsLoader, Depends()],
        extractor: Annotated[Extractor, Depends()]
) -> RequirementsValidator:
    return RequirementsValidator(
        requirements_loader=requirements_loader,
        extractor=extractor
    )