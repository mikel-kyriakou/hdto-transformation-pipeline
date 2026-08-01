from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.models.enums import Source
from app.pipeline.protocols.source_identifier import SourceIdentifierProtocol
from app.services.identify_source import IdentifySourceService
from app.services.file_reader import FileReader
from app.validation.validator import RequirementsValidator


class BasePipeline(ABC):
    def __init__(
            self,
            file_reader: FileReader,
            source_identifier: IdentifySourceService,
            requirements_validator: RequirementsValidator
    ) -> None:
        self.file_reader = file_reader
        self.source_identifier = source_identifier
        self.requirements_validator = requirements_validator


    def execute(self, file: UploadFile):
        file_content = self.file_reader.read_file(file)
        
        # heritage_objects = self.get_objects(file_content)

        source = self.source_identifier.identify_source(file_content)

        # pipeline = self.build_pipeline(source)

        self.requirements_validator.validate(source, file_content)

        mappings = pipeline.map_to_rhdto(file_content)

        instances = pipeline.create_instances(mappings)

        return self.create_output_file(instances)


    def identify_source(self, objects: list) -> Source:
        pass

    def get_objects(self, file_content: dict | list) -> list:
        pass

    # TODO use factory pattern
    def build_pipeline(self, source) -> BasePipeline:
        pass

    @abstractmethod
    def has_minimum_required_fields(self, objects: list) -> bool: 
        pass

    @abstractmethod
    def map_to_rhdto(self, objects: list) -> list:
        pass

    @abstractmethod
    def create_instances(self, mappings: list) -> list:
        pass

    @abstractmethod
    def create_output_file(self, instances: list) -> bytes:
        pass