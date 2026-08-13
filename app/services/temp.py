from fastapi import UploadFile, Depends
from typing import Annotated

from app.services.file_reader import FileReader
from app.services.identify_source import IdentifySourceService
from app.transformation.transformer import Transformer, get_transformer
from app.validation.validator import RequirementsValidator, get_requirements_validator


class TempService:

    def __init__(
            self, 
            file_reader: FileReader,
            source_identifier: IdentifySourceService,
            validator: RequirementsValidator,
            transformer: Transformer
    ) -> None:
        self.file_reader = file_reader
        self.source_identifier = source_identifier
        self.validator = validator
        self.transformer = transformer

    async def run(self, file: UploadFile) -> list:
        file_content = await self.file_reader.read_file(file)
        source = self.source_identifier.identify_source(file_content)
        self.validator.validate(source, file_content)
        objects = self.transformer.transform(source, file_content)

        return objects

def get_temp_service(
        file_reader: Annotated[FileReader, Depends()],
        source_identifier: Annotated[IdentifySourceService, Depends()],
        validator: Annotated[RequirementsValidator, Depends(get_requirements_validator)],
        transformer: Annotated[Transformer, Depends(get_transformer)]
) -> TempService:
    return TempService(
        file_reader,
        source_identifier,
        validator,
        transformer
    )