from typing import Annotated
from fastapi import Depends

from app.rules.loader import RulesLoader
from app.extraction.extractor import Extractor
from app.models.enums import Source
from app.models.models import HeritageObjectData, Actor, Collection, Place


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
                    id=self.extractor.extract(record, mapping_rules['id']['PATH'], strategy=mapping_rules['id'].get('STRATEGY')),
                    title=self.extractor.extract(record, mapping_rules['title']['PATH'], strategy=mapping_rules['title'].get('STRATEGY')),
                    description=self.extractor.extract(record, mapping_rules['description']['PATH'], strategy=mapping_rules['description'].get('STRATEGY')),
                    object_type=self.extractor.extract(record, mapping_rules['object_type']['PATH'], strategy=mapping_rules['object_type'].get('STRATEGY')),
                    material=self.extractor.extract(record, mapping_rules['material']['PATH'], strategy=mapping_rules['material'].get('STRATEGY')),
                    collections=self._create_collections(
                        ids=self.extractor.extract(record, mapping_rules['collections']['id']['PATH']),
                        titles=self.extractor.extract(record, mapping_rules['collections']['title']['PATH']),
                        descriptions=self.extractor.extract(record, mapping_rules['collections']['description']['PATH'])
                    ),
                    representation=self.extractor.extract(record, mapping_rules['representation']['PATH'], strategy=mapping_rules['representation'].get('STRATEGY')),
                    depiction=self.extractor.extract(record, mapping_rules['depiction']['PATH'], strategy=mapping_rules['depiction'].get('STRATEGY')),
                    part_of=self.extractor.extract(record, mapping_rules['part_of']['PATH'], strategy=mapping_rules['part_of'].get('STRATEGY')),
                    language=self.extractor.extract(record, mapping_rules['language']['PATH'], strategy=mapping_rules['language'].get('STRATEGY')),
                    reference=self.extractor.extract(record, mapping_rules['reference']['PATH'], strategy=mapping_rules['reference'].get('STRATEGY')),
                    creation_date=self.extractor.extract(record, mapping_rules['creation_date']['PATH'], strategy=mapping_rules['creation_date'].get('STRATEGY')),
                    destruction_date=self.extractor.extract(record, mapping_rules['destruction_date']['PATH'], strategy=mapping_rules['destruction_date'].get('STRATEGY')),
                    place_of_creation=self._create_place(
                        name=self.extractor.extract(record, mapping_rules['place_of_creation']['name']['PATH'], strategy=mapping_rules['place_of_creation']['name'].get('STRATEGY')),
                        latitude=self.extractor.extract(record, mapping_rules['place_of_creation']['latitude']['PATH'], strategy=mapping_rules['place_of_creation']['latitude'].get('STRATEGY')),
                        longitude=self.extractor.extract(record, mapping_rules['place_of_creation']['longitude']['PATH'], strategy=mapping_rules['place_of_creation']['longitude'].get('STRATEGY'))
                    ),
                    place_of_destruction=self._create_place(
                        name=self.extractor.extract(record, mapping_rules['place_of_destruction']['name']['PATH'], strategy=mapping_rules['place_of_destruction']['name'].get('STRATEGY')),
                        latitude=self.extractor.extract(record, mapping_rules['place_of_destruction']['latitude']['PATH'], strategy=mapping_rules['place_of_destruction']['latitude'].get('STRATEGY')),
                        longitude=self.extractor.extract(record, mapping_rules['place_of_destruction']['longitude']['PATH'], strategy=mapping_rules['place_of_destruction']['longitude'].get('STRATEGY'))
                    ),
                    created_by=self._create_actors(
                        ids=self.extractor.extract(record, mapping_rules['created_by']['id']['PATH'], strategy=mapping_rules['created_by']['id'].get('STRATEGY')),
                        names=self.extractor.extract(record, mapping_rules['created_by']['name']['PATH'], strategy=mapping_rules['created_by']['name'].get('STRATEGY'))
                    ),
                    digital_representation=self.extractor.extract(record, mapping_rules['digital_representation']['PATH'], strategy=mapping_rules['digital_representation'].get('STRATEGY'))
                )
            )
            
        return transformed_records

    def _create_actors(self, ids: list[str] | str | None, names: list[str] | str | None) -> list[Actor]:
        if isinstance(ids, str):
            ids = [ids]
        elif ids is None:
            ids = []
        
        if isinstance(names, str):
            names = [names]
        elif names is None:
            names = []

        size = max(len(ids), len(names))

        actors = []
        for index in range(size):
            actors.append(Actor(
                id=ids[index] if len(ids) > index else None,
                name=names[index] if len(names) > index else None
            ))

        return actors

    def _create_collections(self, ids: list[str] | None, titles: list[str] | None, descriptions: list[str] | None) -> list[Collection]:
        ids = ids or []
        titles = titles or []
        descriptions = descriptions or []
        size = max(len(ids), len(titles), len(descriptions))

        collections = []

        for index in range(size):
            collections.append(Collection(
                id=ids[index] if len(ids) > index else None,
                title=titles[index] if len(titles) > index else None,
                description=descriptions[index] if len(descriptions) > index else None
            ))

        return collections

    def _create_place(self, name: str | None, longitude: float | None, latitude: float | None) -> Place | None:
        if not name and (not latitude or not longitude):
            return None

        return Place(
            name=name or None,
            latitude=latitude or None,
            longitude=longitude or None
        )

def get_transformer(
        loader: Annotated[RulesLoader, Depends()],
        extractor: Annotated[Extractor, Depends()]
) -> Transformer:
    return Transformer(loader, extractor)