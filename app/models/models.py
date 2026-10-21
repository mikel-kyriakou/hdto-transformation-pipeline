import json

from pydantic import BaseModel

from app.models.enums import MediaType
from app.models.enums import Source


class DigitalFile(BaseModel):
    representation: str
    file_type: str | None = None
    format: str | None = None
    

class CustomMetadata(BaseModel):
    id: str | None
    title: str | None
    object_type: str | None
    creator: str | None
    date_of_creation: str | None
    place_of_creation: str | None
    material: str | None
    dimensions: str | None
    cultural_period: str | None 
    digital_file: DigitalFile | None


class Collection(BaseModel):
    id: str | None = None
    title: str | None = None
    description: str | None = None


class Actor(BaseModel):
    id: str | None = None
    name: str | None = None

class Place(BaseModel):
    name: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class HeritageObjectData(BaseModel):
    id: str | None = None
    title: str | list[str] | None = None
    description: str | list[str] | None  = None

    object_type: str | list[str] | None = None
    material: str | list[str] | None = None

    # dimensions: 

    collections: list[Collection] | None = None

    representation: str | None = None #the id of the digital file representation
    # depiction: str | None = None #the id of the digital file depiction | is this the same with representation?
    # part_of: str | None = None #the id of the heritage object that this object is part of

    language: str | list[str] | None = None
    reference: str | None = None

    creation_date: str | None = None
    destruction_date: str | None = None

    place_of_creation: Place | None = None
    place_of_destruction: Place | None = None

    created_by: list[Actor] | None = None

    digital_representation: str | None = None #the 3d model

class InvalidRecordsData(BaseModel):
    index: int
    content: dict
    missing_fields: list[str]

class PipelineMetrics(BaseModel):
    identified_source: Source | None = None
    records_processed: int | None = None
    records_valid: int | None = None
    records_invalid: int | None = None
    triples_generated: int | None = None
    duration_s: int | float | None = None
    items_per_class: dict[str, int] = {}
    invalid_records_data: list[InvalidRecordsData] | None = None

class PipelineResponse(BaseModel):
    content: str
    format: MediaType
    metrics: PipelineMetrics
    triples: list[dict[str, str]]