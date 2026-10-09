import time
from fastapi import UploadFile, Depends
from typing import Annotated

from app.services.identify_source import IdentifySourceService
from app.services.file_reader import FileReader
from app.validation.validator import RequirementsValidator, get_requirements_validator
from app.transformation.transformer import Transformer, get_transformer
from app.mapping.mapper import Mapper, get_mapper
from app.models.enums import OutputFormat
from app.models.models import PipelineResponse
from app.models.models import PipelineMetrics
from app.metrics.metrics_generator import MetricsGenerator


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

    async def execute(self, file: UploadFile, output_format: OutputFormat) -> PipelineResponse:
        start = time.perf_counter()

        file_content = await self.file_reader.read_file(file)
        if isinstance(file_content, dict):
            raise Exception("Invalid input")

        source = self.source_identifier.identify_source(file_content)

        validated_objects = self.requirements_validator.validate(source, file_content)

        intermediate_objects = self.transformer.transform(source, validated_objects)

        graph = self.mapper.map(intermediate_objects)

        return PipelineResponse(
            content=graph.serialize(format=output_format),
            format=output_format.media_type,
            triples=[
                {
                    "subject": subject.n3(),
                    "subject_label": str(subject),
                    "subject_kind": type(subject).__name__,
                    "predicate": predicate.n3(),
                    "predicate_label": str(predicate),
                    "object": object_.n3(),
                    "object_label": str(object_),
                    "object_kind": type(object_).__name__,
                }
                for subject, predicate, object_ in graph
            ],
            metrics=PipelineMetrics(
                identified_source=source,
                records_processed=len(file_content),
                records_valid=len(validated_objects),
                records_invalid=len(file_content)-len(validated_objects),
                triples_generated=len(graph),
                duration_s=round(time.perf_counter() - start, 3),
                items_per_class=MetricsGenerator.items_per_class(graph)
            )
        )

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