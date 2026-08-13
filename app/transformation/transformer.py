from typing import Annotated
from fastapi import Depends

from app.rules.loader import RulesLoader
from app.extraction.extractor import Extractor
from app.models.enums import Source
from app.models.models import HeritageObjectData, Actor, CollectionData


class Transformer:

    def __init__(self, loader: RulesLoader, extractor: Extractor) -> None:
        self.loader = loader
        self.extractor = extractor

    def transform(self, source: Source, file_content: list) -> list[HeritageObjectData]:
        mapping_rules = self.loader.load_mapping_rules(source)

        transformed_records = []
        for record in file_content:
            
            transformed_records.append(
                HeritageObjectData(
                    id=self.extractor.extract(record, mapping_rules['id']['PATH']),
                    title=self.extractor.extract(record, mapping_rules['title']['PATH'], strategy=mapping_rules['title'].get('STRATEGY')),
                    object_type=self.extractor.extract(record, mapping_rules['object_type']['PATH'], strategy=mapping_rules['object_type'].get('STRATEGY')),
                    material=self.extractor.extract(record, mapping_rules['material']['PATH'], strategy=mapping_rules['material'].get('STRATEGY')),
                    collections=[],
                    representation=self.extractor.extract(record, mapping_rules['representation']['PATH']),
                    depiction=self.extractor.extract(record, mapping_rules['depiction']['PATH']),
                    part_of=self.extractor.extract(record, mapping_rules['part_of']['PATH']),
                    language=self.extractor.extract(record, mapping_rules['language']['PATH'], strategy=mapping_rules['language'].get('STRATEGY')),
                    reference=self.extractor.extract(record, mapping_rules['reference']['PATH']),
                    creation_date=self.extractor.extract(record, mapping_rules['creation_date']['PATH'], strategy=mapping_rules['creation_date'].get('STRATEGY')),
                    destruction_date=self.extractor.extract(record, mapping_rules['destruction_date']['PATH'], strategy=mapping_rules['destruction_date'].get('STRATEGY')),
                    place_of_creation=self.extractor.extract(record, mapping_rules['place_of_creation']['PATH'], strategy=mapping_rules['place_of_creation'].get('STRATEGY')),
                    place_of_destruction=self.extractor.extract(record, mapping_rules['place_of_destruction']['PATH'], strategy=mapping_rules['place_of_destruction'].get('STRATEGY')),
                    created_by=self.create_actors(self.extractor.extract(record, mapping_rules['created_by']['name']['PATH'], strategy=mapping_rules['created_by']['name'].get('STRATEGY'))),
                    digital_representation=self.extractor.extract(record, mapping_rules['digital_representation']['PATH'])
                )
            )
            
        return transformed_records

    def create_actors(self, value: list | str) -> list[Actor]:
        if value is None:
            return []
        
        if isinstance(value, str):
            value = [value]

        actors = []
        for actor in value:
            actors.append(Actor(name=actor))

        return actors

def get_transformer(
        loader: Annotated[RulesLoader, Depends()],
        extractor: Annotated[Extractor, Depends()]
) -> Transformer:
    return Transformer(loader, extractor)

if __name__ == "__main__":
    loader = RulesLoader()
    extractor = Extractor()
    transformer = Transformer(loader, extractor)

    # Example usage
    source = Source.DPLA
    file_content = [
    {
        "@context": "http://dp.la/api/items/context",
        "@id": "http://dp.la/api/items/7fe6a4204ac031547de1c524420a5bea",
        "@type": "ore:Aggregation",
        "aggregatedCHO": "#sourceResource",
        "dataProvider": {
            "@id": "http://dp.la/api/contributor/state-historical-society-of-missouri",
            "exactMatch": [
                "http://www.wikidata.org/entity/Q7603366"
            ],
            "name": "State Historical Society of Missouri"
        },
        "id": "7fe6a4204ac031547de1c524420a5bea",
        "iiifManifest": "http://cdm17228.contentdm.oclc.org/iiif/info/ec/6479/manifest.json",
        "ingestDate": "2026-01-15T17:44:49.351Z",
        "ingestType": "item",
        "isShownAt": "http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479",
        "object": "http://cdm17228.contentdm.oclc.org/utils/getthumbnail/collection/ec/id/6479",
        "originalRecord": {
            "stringValue": "{\n  \"@context\" : \"http://dp.la/api/items/context\",\n  \"isShownAt\" : \"http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479\",\n  \"dataProvider\" : \"State Historical Society of Missouri\",\n  \"@type\" : \"ore:Aggregation\",\n  \"hasView\" : {\n    \"@id\" : \"http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479\"\n  },\n  \"provider\" : {\n    \"@id\" : \"http://dp.la/api/contributor/missouri-hub\",\n    \"name\" : \"Missouri Hub\"\n  },\n  \"object\" : \"http://cdm17228.contentdm.oclc.org/utils/getthumbnail/collection/ec/id/6479\",\n  \"aggregatedCHO\" : \"#sourceResource\",\n  \"sourceResource\" : {\n    \"title\" : [ \"After World War II. After World War III - - - ?\" ],\n    \"description\" : [ \"A man is shown pushing \\\"Japan\\\" and \\\"Germany\\\" in a baby carriage.\" ],\n    \"subject\" : [ {\n      \"name\" : \"International relations\"\n    }, {\n      \"name\" : \"Japan\"\n    }, {\n      \"name\" : \"Germany\"\n    } ],\n    \"temporal\" : [ {\n      \"displayDate\" : \"1954-08-09\"\n    } ],\n    \"identifier\" : [ \"http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479\" ],\n    \"creator\" : [ \"Fitzpatrick, Daniel Robert, 1891-1969\" ],\n    \"language\" : [ ],\n    \"rights\" : \"Permission to reproduce can be obtained through the State Historical Society of Missouri\",\n    \"@id\" : \"oai:cdm17228.contentdm.oclc.org:ec/6479\",\n    \"format\" : \"Mechanical prints; Editorial Cartoons\"\n  },\n  \"@id\" : \"missouri--urn:data.mohistory.org:ec:oai:cdm17228.contentdm.oclc.org:ec/6479\",\n  \"iiifManifest\" : \"http://cdm17228.contentdm.oclc.org/iiif/info/ec/6479/manifest.json\"\n}"
        },
        "provider": {
            "@id": "http://dp.la/api/contributor/heartland-hub",
            "exactMatch": [
                "http://www.wikidata.org/entity/Q83878488"
            ],
            "name": "Heartland Hub"
        },
        "rightsCategory": "Unspecified Rights Status",
        "sourceResource": {
            "@id": "http://dp.la/api/items/7fe6a4204ac031547de1c524420a5bea#SourceResource",
            "creator": [
                "Fitzpatrick, Daniel Robert, 1891-1969"
            ],
            "date": [
                {
                    "displayDate": "1954-08-09"
                }
            ],
            "description": [
                "A man is shown pushing \"Japan\" and \"Germany\" in a baby carriage."
            ],
            "format": [
                "Mechanical prints; Editorial Cartoons"
            ],
            "identifier": [
                "http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479"
            ],
            "rights": [
                "Permission to reproduce can be obtained through the State Historical Society of Missouri"
            ],
            "subject": [
                {
                    "name": "International relations"
                },
                {
                    "name": "Japan"
                },
                {
                    "name": "Germany"
                }
            ],
            "title": [
                "After World War II. After World War III?"
            ]
        }
    }
    ]

    source = Source.CUSTOM
    file_content = [
        {
            "id": "DA-01",
            "title": "Dora Arch - Part 1",
            "object_type": "Ornamental Arch Fragment",
            "creator": "Anonymous",
            "date_of_creation": "c. 1200–1350 AD",
            "place_of_creation": "Trondheim, Norway",
            "material": "Soapstone",
            "dimensions": "45 x 20 x 15 cm",
            "cultural_period": "High Gothic",
            "digital_file": {
                "file_url": "https://graphics.cs.aueb.gr/graphics/viewer2.html?item=DoraArch1.glb&fov=25&ground=0.0",
                "file_type": "3D Mesh",
                "format": "OBJ",
                "representation": "High-resolution Surface Scan"
            }
        }
    ]

    transformed_data = transformer.transform(source, file_content)
    for data in transformed_data:
        print(data)