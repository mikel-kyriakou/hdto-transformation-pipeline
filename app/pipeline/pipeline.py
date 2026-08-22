from fastapi import UploadFile, Depends
from typing import Annotated

from app.services.identify_source import IdentifySourceService
from app.services.file_reader import FileReader
from app.validation.validator import RequirementsValidator, get_requirements_validator
from app.transformation.transformer import Transformer, get_transformer
from app.mapping.mapper import Mapper, get_mapper
from app.models.enums import OutputFormat


class Pipeline:
    def __init__(
            self,
            file_reader: FileReader,
            source_identifier: IdentifySourceService,
            requirements_validator: RequirementsValidator,
            transformer: Transformer,
            mapper: Mapper
    ) -> None:
        self.file_reader = file_reader
        self.source_identifier = source_identifier
        self.requirements_validator = requirements_validator
        self.transformer = transformer
        self.mapper = mapper

    async def execute(self, file: UploadFile, output_format: OutputFormat):
        file_content = await self.file_reader.read_file(file)
        
        source = self.source_identifier.identify_source(file_content)

        self.requirements_validator.validate(source, file_content)

        intermediate_objects = self.transformer.transform(source, file_content)

        graph = self.mapper.map(intermediate_objects)

        return graph.serialize(format=output_format)

def build_pipeline(
        file_reader: Annotated[FileReader, Depends()],
        source_identifier: Annotated[IdentifySourceService, Depends()],
        requirements_validator: Annotated[RequirementsValidator, Depends(get_requirements_validator)],
        transformer: Annotated[Transformer, Depends(get_transformer)],
        mapper: Annotated[Mapper, Depends(get_mapper)]
) -> Pipeline:
    return Pipeline(
        file_reader=file_reader,
        source_identifier=source_identifier,
        requirements_validator=requirements_validator,
        transformer=transformer,
        mapper=mapper
    )