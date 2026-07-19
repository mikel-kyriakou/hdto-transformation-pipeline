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