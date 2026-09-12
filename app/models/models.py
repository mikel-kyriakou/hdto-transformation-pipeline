from pydantic import BaseModel


class DigitalFile(BaseModel):
    file_type: str
    format: str
    representation: str


class CustomMetadata(BaseModel):
    id: str
    title: str
    object_type: str
    creator: str
    date_of_creation: str
    place_of_creation: str
    material: str
    dimensions: str
    cultural_period: str
    digital_file: DigitalFile


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
    depiction: str | None = None #the id of the digital file depiction | is this the same with representation?
    part_of: str | None = None #the id of the heritage object that this object is part of

    language: str | list[str] | None = None
    reference: str | None = None

    creation_date: str | None = None
    destruction_date: str | None = None

    place_of_creation: Place | None = None
    place_of_destruction: Place | None = None

    created_by: list[Actor] | None = None

    digital_representation: str | None = None #the 3d model