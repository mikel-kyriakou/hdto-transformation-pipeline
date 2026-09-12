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
                    collections=self.create_colletions(
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
                    place_of_creation=self.create_place(
                        name=self.extractor.extract(record, mapping_rules['place_of_creation']['name']['PATH'], strategy=mapping_rules['place_of_creation']['name'].get('STRATEGY')),
                        latitude=self.extractor.extract(record, mapping_rules['place_of_creation']['latitude']['PATH'], strategy=mapping_rules['place_of_creation']['latitude'].get('STRATEGY')),
                        longitude=self.extractor.extract(record, mapping_rules['place_of_creation']['longitude']['PATH'], strategy=mapping_rules['place_of_creation']['longitude'].get('STRATEGY'))
                    ),
                    place_of_destruction=self.create_place(
                        name=self.extractor.extract(record, mapping_rules['place_of_destruction']['name']['PATH'], strategy=mapping_rules['place_of_destruction']['name'].get('STRATEGY')),
                        latitude=self.extractor.extract(record, mapping_rules['place_of_destruction']['latitude']['PATH'], strategy=mapping_rules['place_of_destruction']['latitude'].get('STRATEGY')),
                        longitude=self.extractor.extract(record, mapping_rules['place_of_destruction']['longitude']['PATH'], strategy=mapping_rules['place_of_destruction']['longitude'].get('STRATEGY'))
                    ),
                    created_by=self.create_actors(
                        ids=self.extractor.extract(record, mapping_rules['created_by']['id']['PATH'], strategy=mapping_rules['created_by']['id'].get('STRATEGY')),
                        names=self.extractor.extract(record, mapping_rules['created_by']['name']['PATH'], strategy=mapping_rules['created_by']['name'].get('STRATEGY'))
                    ),
                    digital_representation=self.extractor.extract(record, mapping_rules['digital_representation']['PATH'], strategy=mapping_rules['digital_representation'].get('STRATEGY'))
                )
            )
            
        return transformed_records

    def create_actors(self, ids: list[str] | str | None, names: list[str] | str | None) -> list[Actor]:
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

    def create_colletions(self, ids: list[str] | None, titles: list[str] | None, descriptions: list[str] | None) -> list[Collection]:
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

    def create_place(self, name: str | None, longitude: float | None, latitude: float | None) -> Place | None:
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

if __name__ == "__main__":
    loader = RulesLoader()
    extractor = Extractor()
    transformer = Transformer(loader, extractor)

    # Example usage
    # source = Source.DPLA
    # file_content = [
    # {
    #     "@context": "http://dp.la/api/items/context",
    #     "@id": "http://dp.la/api/items/7fe6a4204ac031547de1c524420a5bea",
    #     "@type": "ore:Aggregation",
    #     "aggregatedCHO": "#sourceResource",
    #     "dataProvider": {
    #         "@id": "http://dp.la/api/contributor/state-historical-society-of-missouri",
    #         "exactMatch": [
    #             "http://www.wikidata.org/entity/Q7603366"
    #         ],
    #         "name": "State Historical Society of Missouri"
    #     },
    #     "id": "7fe6a4204ac031547de1c524420a5bea",
    #     "iiifManifest": "http://cdm17228.contentdm.oclc.org/iiif/info/ec/6479/manifest.json",
    #     "ingestDate": "2026-01-15T17:44:49.351Z",
    #     "ingestType": "item",
    #     "isShownAt": "http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479",
    #     "object": "http://cdm17228.contentdm.oclc.org/utils/getthumbnail/collection/ec/id/6479",
    #     "originalRecord": {
    #         "stringValue": "{\n  \"@context\" : \"http://dp.la/api/items/context\",\n  \"isShownAt\" : \"http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479\",\n  \"dataProvider\" : \"State Historical Society of Missouri\",\n  \"@type\" : \"ore:Aggregation\",\n  \"hasView\" : {\n    \"@id\" : \"http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479\"\n  },\n  \"provider\" : {\n    \"@id\" : \"http://dp.la/api/contributor/missouri-hub\",\n    \"name\" : \"Missouri Hub\"\n  },\n  \"object\" : \"http://cdm17228.contentdm.oclc.org/utils/getthumbnail/collection/ec/id/6479\",\n  \"aggregatedCHO\" : \"#sourceResource\",\n  \"sourceResource\" : {\n    \"title\" : [ \"After World War II. After World War III - - - ?\" ],\n    \"description\" : [ \"A man is shown pushing \\\"Japan\\\" and \\\"Germany\\\" in a baby carriage.\" ],\n    \"subject\" : [ {\n      \"name\" : \"International relations\"\n    }, {\n      \"name\" : \"Japan\"\n    }, {\n      \"name\" : \"Germany\"\n    } ],\n    \"temporal\" : [ {\n      \"displayDate\" : \"1954-08-09\"\n    } ],\n    \"identifier\" : [ \"http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479\" ],\n    \"creator\" : [ \"Fitzpatrick, Daniel Robert, 1891-1969\" ],\n    \"language\" : [ ],\n    \"rights\" : \"Permission to reproduce can be obtained through the State Historical Society of Missouri\",\n    \"@id\" : \"oai:cdm17228.contentdm.oclc.org:ec/6479\",\n    \"format\" : \"Mechanical prints; Editorial Cartoons\"\n  },\n  \"@id\" : \"missouri--urn:data.mohistory.org:ec:oai:cdm17228.contentdm.oclc.org:ec/6479\",\n  \"iiifManifest\" : \"http://cdm17228.contentdm.oclc.org/iiif/info/ec/6479/manifest.json\"\n}"
    #     },
    #     "provider": {
    #         "@id": "http://dp.la/api/contributor/heartland-hub",
    #         "exactMatch": [
    #             "http://www.wikidata.org/entity/Q83878488"
    #         ],
    #         "name": "Heartland Hub"
    #     },
    #     "rightsCategory": "Unspecified Rights Status",
    #     "sourceResource": {
    #         "@id": "http://dp.la/api/items/7fe6a4204ac031547de1c524420a5bea#SourceResource",
    #         "collection": [
    #             {
    #                 "title": "W. E. B. Du Bois Papers"
    #             }
    #         ],
    #         "creator": [
    #             "Fitzpatrick, Daniel Robert, 1891-1969"
    #         ],
    #         "date": [
    #             {
    #                 "displayDate": "1954-08-09"
    #             }
    #         ],
    #         "description": [
    #             "A man is shown pushing \"Japan\" and \"Germany\" in a baby carriage."
    #         ],
    #         "format": [
    #             "Mechanical prints; Editorial Cartoons"
    #         ],
    #         "identifier": [
    #             "http://cdm17228.contentdm.oclc.org/cdm/ref/collection/ec/id/6479"
    #         ],
    #         "rights": [
    #             "Permission to reproduce can be obtained through the State Historical Society of Missouri"
    #         ],
    #         "subject": [
    #             {
    #                 "name": "International relations"
    #             },
    #             {
    #                 "name": "Japan"
    #             },
    #             {
    #                 "name": "Germany"
    #             }
    #         ],
    #         "title": [
    #             "After World War II. After World War III?"
    #         ]
    #     }
    # }
    # ]

    # source = Source.CUSTOM
    # file_content = [
    #     {
    #         "id": "DA-01",
    #         "title": "Dora Arch - Part 1",
    #         "object_type": "Ornamental Arch Fragment",
    #         "creator": "Anonymous",
    #         "date_of_creation": "c. 1200–1350 AD",
    #         "place_of_creation": "Trondheim, Norway",
    #         "material": "Soapstone",
    #         "dimensions": "45 x 20 x 15 cm",
    #         "cultural_period": "High Gothic",
    #         "digital_file": {
    #             "file_url": "https://graphics.cs.aueb.gr/graphics/viewer2.html?item=DoraArch1.glb&fov=25&ground=0.0",
    #             "file_type": "3D Mesh",
    #             "format": "OBJ",
    #             "representation": "High-resolution Surface Scan"
    #         }
    #     }
    # ]

    file_content = [{
    "about": "/181/share3d_2327",
    "aggregations": [
        {
            "about": "/aggregation/provider/181/share3d_2327",
            "edmDataProvider": {
                "def": [
                    "http://data.europeana.eu/organization/5392"
                ]
            },
            "edmIsShownBy": "https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd/embed",
            "edmIsShownAt": "https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd",
            "edmObject": "https://media.sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd/thumbnails/46674cf7bd584c8996a59fe229b1484d/8e3bb9c22fb3434fb8e2f33e233ec7e0.jpeg",
            "edmProvider": {
                "def": [
                    "http://data.europeana.eu/organization/1617"
                ]
            },
            "edmRights": {
                "def": [
                    "http://creativecommons.org/licenses/by-sa/4.0/"
                ]
            },
            "edmUgc": "false",
            "aggregatedCHO": "/item/181/share3d_2327",
            "webResources": [
                {
                    "about": "https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd/embed",
                    "dcDescription": {
                        "nl": [
                            "Made with 3DF Zephyr photogrammetry software."
                        ]
                    },
                    "dcFormat": {
                        "en": [
                            "glTF"
                        ]
                    },
                    "dctermsCreated": {
                        "def": [
                            "2025"
                        ]
                    },
                    "dcCreator": {
                        "def": [
                            "Archeologiemuseum Huis van Hilde, Kees Zwaan"
                        ]
                    },
                    "dcType": {
                        "en": [
                            "3D"
                        ]
                    },
                    "textAttributionSnippet": "(en) Butter churn (ca. 1650) - https://www.europeana.eu/item/181/share3d_2327. Archeologiemuseum Huis van Hilde, Kees Zwaan. Huis van Hilde - https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd. CC BY-SA - http://creativecommons.org/licenses/by-sa/4.0/",
                    "htmlAttributionSnippet": "<link rel='stylesheet' type='text/css' href='https://api.europeana.eu/attribution/style.css'/><dl class='europeana-attribution' lang='en'><dt>Title</dt><dd lang='en'><a href='http://data.europeana.eu/item/181/share3d_2327' target='_blank' rel='noopener'>Butter churn (ca. 1650)</a></dd><dt>Creator</dt><dd lang=''>Archeologiemuseum Huis van Hilde, Kees Zwaan</dd><dt>Date</dt><dd lang=''>2025</dd><dt>Institution</dt><dd lang=''><a href='https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd' target='_blank' rel='noopener'>Huis van Hilde</a></dd><dt>Country</dt><dd lang=''>Netherlands</dd><dt>Rights</dt><dd><a href='http://creativecommons.org/licenses/by-sa/4.0/' target='_blank' rel='noopener'><span class='icon-cc'/><span class='icon-by'/><span class='icon-sa'/>CC BY-SA</a></dd></dl>",
                    "rdfType": "http://www.europeana.eu/schemas/edm/FullTextResource",
                    "ebucoreHasMimeType": "text/html",
                    "ebucoreFileByteSize": 108322
                },
                {
                    "about": "https://media.sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd/thumbnails/46674cf7bd584c8996a59fe229b1484d/8e3bb9c22fb3434fb8e2f33e233ec7e0.jpeg",
                    "textAttributionSnippet": "(en) Butter churn (ca. 1650) - https://www.europeana.eu/item/181/share3d_2327. Archeologiemuseum Huis van Hilde, Kees Zwaan. Huis van Hilde - https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd. CC BY-SA - http://creativecommons.org/licenses/by-sa/4.0/",
                    "htmlAttributionSnippet": "<link rel='stylesheet' type='text/css' href='https://api.europeana.eu/attribution/style.css'/><dl class='europeana-attribution' lang='en'><dt>Title</dt><dd lang='en'><a href='http://data.europeana.eu/item/181/share3d_2327' target='_blank' rel='noopener'>Butter churn (ca. 1650)</a></dd><dt>Creator</dt><dd lang=''>Archeologiemuseum Huis van Hilde, Kees Zwaan</dd><dt>Date</dt><dd lang=''>2025</dd><dt>Institution</dt><dd lang=''><a href='https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd' target='_blank' rel='noopener'>Huis van Hilde</a></dd><dt>Country</dt><dd lang=''>Netherlands</dd><dt>Rights</dt><dd><a href='http://creativecommons.org/licenses/by-sa/4.0/' target='_blank' rel='noopener'><span class='icon-cc'/><span class='icon-by'/><span class='icon-sa'/>CC BY-SA</a></dd></dl>",
                    "ebucoreHasMimeType": "image/jpeg",
                    "ebucoreFileByteSize": 130678,
                    "ebucoreWidth": 1920,
                    "ebucoreHeight": 1080,
                    "edmHasColorSpace": "sRGB",
                    "edmComponentColor": [
                        "#DCDCDC",
                        "#D3D3D3",
                        "#808080",
                        "#BDB76B",
                        "#696969",
                        "#C0C0C0"
                    ],
                    "ebucoreOrientation": "landscape"
                },
                {
                    "about": "https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd",
                    "textAttributionSnippet": "(en) Butter churn (ca. 1650) - https://www.europeana.eu/item/181/share3d_2327. Archeologiemuseum Huis van Hilde, Kees Zwaan. Huis van Hilde - https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd. CC BY-SA - http://creativecommons.org/licenses/by-sa/4.0/",
                    "htmlAttributionSnippet": "<link rel='stylesheet' type='text/css' href='https://api.europeana.eu/attribution/style.css'/><dl class='europeana-attribution' lang='en'><dt>Title</dt><dd lang='en'><a href='http://data.europeana.eu/item/181/share3d_2327' target='_blank' rel='noopener'>Butter churn (ca. 1650)</a></dd><dt>Creator</dt><dd lang=''>Archeologiemuseum Huis van Hilde, Kees Zwaan</dd><dt>Date</dt><dd lang=''>2025</dd><dt>Institution</dt><dd lang=''><a href='https://sketchfab.com/models/b135c38a0a1e414784c6db4469501bfd' target='_blank' rel='noopener'>Huis van Hilde</a></dd><dt>Country</dt><dd lang=''>Netherlands</dd><dt>Rights</dt><dd><a href='http://creativecommons.org/licenses/by-sa/4.0/' target='_blank' rel='noopener'><span class='icon-cc'/><span class='icon-by'/><span class='icon-sa'/>CC BY-SA</a></dd></dl>",
                    "ebucoreHasMimeType": "text/html",
                    "ebucoreFileByteSize": 0
                }
            ],
            "dqvHasQualityAnnotation": [
                {
                    "created": "2025-12-08T13:57:26.048177289Z",
                    "target": [
                        "/aggregation/provider/181/share3d_2327"
                    ],
                    "body": "http://www.europeana.eu/schemas/epf/contentTier4"
                },
                {
                    "created": "2025-12-08T13:57:26.048200172Z",
                    "target": [
                        "/aggregation/provider/181/share3d_2327"
                    ],
                    "body": "http://www.europeana.eu/schemas/epf/metadataTierC"
                }
            ]
        }
    ],
    "concepts": [ 
        {
            "about": "http://data.europeana.eu/concept/1766",
            "prefLabel": {
                "def": [
                    "Metal"
                ],
                "ru": [
                    "Металл"
                ]
            }
        },
        {
            "about": "http://vocab.getty.edu/aat/300082981",
            "prefLabel": {
                "de": [
                    "Schiff"
                ],
                "en": [
                    "ships"
                ],
                "fr": [
                    "navire"
                ],
                "es": [
                    "barcos"
                ],
                "nl": [
                    "schepen"
                ]
            },
            "altLabel": {
                "de": [
                    "Schiffe"
                ],
                "en": [
                    "ship"
                ],
                "nl": [
                    "schip"
                ],
                "es": [
                    "nave",
                    "barco",
                    "nao"
                ]
            },
            "note": {
                "de": [
                    "Wasserfahrzeug, das gewöhnlich größer und seetüchtiger ist als ein Boot und das gewöhnlich durch Segel oder Motor angetrieben wird."
                ],
                "en": [
                    "Watercraft generally larger and more seaworthy than boats, usually propelled by sails or engines."
                ],
                "nl": [
                    "Over het algemeen te gebruikien voor vaartuigen die groter en zeewaardiger zijn dan boten; worden meestal voortbewogen door zeilen of motoren."
                ],
                "es": [
                    "Úsese para embarcación generalmente más grande y más marinera que los botes, usualmente propulsada por velas o maquinaria."
                ]
            },
            "broader": [
                "http://vocab.getty.edu/aat/300042940"
            ],
            "exactMatch": [
                "http://www.wikidata.org/entity/Q11446"
            ]
        },
        {
            "about": "http://vocab.getty.edu/aat/300387535",
            "prefLabel": {
                "en": [
                    "underwater archaeological sites"
                ],
                "nl": [
                    "archeologische onderwatersites"
                ]
            },
            "altLabel": {
                "en": [
                    "underwater archaeological site",
                    "archaeological sites, underwater"
                ],
                "nl": [
                    "archeologische onderwatersite"
                ]
            },
            "note": {
                "en": [
                    "Sites that are underwater and where archaeological excavations or exploration takes place. Included are shipwrecks, harbor and dock remains, fishing structures, and flooded land sites."
                ],
                "nl": [
                    "Sites die zich onder water bevinden en waar archeologische opgravingen of onderzoekingen plaatsvinden. Voorbeelden zijn scheepswrakken, resten van havens en dokken, constructies om te vissen en overstroomde landsites."
                ]
            },
            "broader": [
                "http://vocab.getty.edu/aat/300000810",
                "http://vocab.getty.edu/aat/300229352"
            ]
        },
        {
            "about": "http://vocab.getty.edu/aat/300234110",
            "prefLabel": {
                "de": [
                    "archäologisches Objekt"
                ],
                "en": [
                    "archaeological objects"
                ],
                "es": [
                    "objetos arqueológicos"
                ],
                "nl": [
                    "archeologische objecten"
                ]
            },
            "altLabel": {
                "de": [
                    "archäologisches Objekt",
                    "archäologische Objekte",
                    "Objekt, archäologisches",
                    "Objekte, archäologische"
                ],
                "en": [
                    "archaeological object",
                    "archaeological materials",
                    "archeological objects",
                    "materials, archaeological",
                    "objects, archaeological"
                ],
                "es": [
                    "objeto arqueológico"
                ],
                "nl": [
                    "oudheidkundige objecten",
                    "oudheidkundig object"
                ]
            },
            "note": {
                "de": [
                    "Im Zusammenhang mit archäologischen Untersuchungen gefundenes Objekt, präziser:  Objekt einer Ausgrabung, gewöhnlich aus Zeiträumen vor dem 19. Jahrundert, nicht mehr existierenden Kulturen zugeordnet. Für Objekte aus gegenwärtigen oder erst kürzlich verschwundenen Kulturen ist bei ethnografischem oder ethnologischem Wert \"Ethnografisches Objekt\" zu verwenden."
                ],
                "en": [
                    "Objects and other material culture found in contexts of archaeological research, typically reserved for those unearthed from periods before usually the 19th century and from extinct cultures. For objects originating in any culture still living or known through relatively recent history when those articles are the concern of ethnographic or ethnological study, prefer \"ethnographic objects.\""
                ],
                "es": [
                    "Úsese para objetos encontrados en el contexto de una investigación arqueológica, más específicamente aquellos exhumados de periodos generalmente anteriores al siglo XIX y de culturas extintas. Para artículos originarios de cualquiera cultura aún con vida o conocida a través de la historia relativamente reciente cuando aquellos artículos son de interés de estudio etnográfico o etnológico, prefiera \"objeto etnográfico”."
                ],
                "nl": [
                    "Te gebruiken voor objecten die zijn gevonden bij archeologisch onderzoek, met name voor opgegraven voorwerpen die stammen uit de periode voor 1800 of voorwerpen uit niet meer bestaande culturen. Gebruik 'etnografica' voor objecten die afkomstig zijn uit een nog bestaande cultuur of bekende cultuur uit het vrij recente verleden, wanneer deze voorwerpen van belang zijn voor etnografische en etnologische onderzoek."
                ]
            },
            "broader": [
                "http://vocab.getty.edu/aat/300185712"
            ],
            "exactMatch": [
                "http://vocab.getty.edu/aat/300117127",
                "http://vocab.getty.edu/aat/300224592",
                "http://www.wikidata.org/entity/Q220659",
                "http://www.wikidata.org/entity/Q16686448"
            ]
        },
        {
            "about": "http://data.europeana.eu/concept/80",
            "prefLabel": {
                "de": [
                    "Archäologie"
                ],
                "fi": [
                    "Arkeologia"
                ],
                "ru": [
                    "Археология"
                ],
                "pt": [
                    "Arqueologia"
                ],
                "bg": [
                    "Археология"
                ],
                "lt": [
                    "Archeologija"
                ],
                "hr": [
                    "Arheologija"
                ],
                "lv": [
                    "Arheoloģija"
                ],
                "fr": [
                    "Archéologie"
                ],
                "hu": [
                    "Régészet"
                ],
                "sk": [
                    "Archeológia"
                ],
                "sl": [
                    "Arheologija"
                ],
                "ga": [
                    "Seandálaíocht"
                ],
                "ca": [
                    "Arqueologia"
                ],
                "sv": [
                    "Arkeologi"
                ],
                "el": [
                    "Αρχαιολογία"
                ],
                "mt": [
                    "Arkeoloġija"
                ],
                "en": [
                    "Archaeology"
                ],
                "it": [
                    "Archeologia"
                ],
                "es": [
                    "Arqueología"
                ],
                "et": [
                    "Arheoloogia"
                ],
                "eu": [
                    "Arkeologia"
                ],
                "cs": [
                    "Archeologie"
                ],
                "pl": [
                    "Archeologia"
                ],
                "da": [
                    "Arkæologi"
                ],
                "ro": [
                    "Arheologie"
                ],
                "nl": [
                    "Archeologie"
                ]
            },
            "note": {
                "de": [
                    "Wissenschaft von den materiellen Hinterlassenschaften früherer Kulturen und ihre Erschließung"
                ],
                "fi": [
                    "Tieteenala, joka tutkii ihmisen historiallisia jäännöksiä"
                ],
                "sv": [
                    "Kunskapen om människans förhistoria"
                ],
                "ru": [
                    "Наука, изучающая историю общества по материальным остаткам жизнедеятельности людей - вещественным памятникам"
                ],
                "pt": [
                    "Estudo do passado através de vestígio material"
                ],
                "mt": [
                    "L-istudju tal-imgħoddi tal-bniedem permezz tal-kultura materjali"
                ],
                "el": [
                    "Συστηματική μελέτη των υλικών καταλοίπων του ανθρώπινου παρελθόντος"
                ],
                "en": [
                    "Study of the past via material culture"
                ],
                "lv": [
                    "Vēstures palīgdisciplīna"
                ],
                "it": [
                    "Scienza che studia le civiltà e le culture umane del passato"
                ],
                "fr": [
                    "Science historique et anthropologique étudiant les sociétés passées par la culture matérielle"
                ],
                "es": [
                    "Ciencia social que estudia los cambios históricos a través de sus vestigios materiales"
                ],
                "et": [
                    "Mineviku uurimine läbi ainelise kultuuripärandi"
                ],
                "eu": [
                    "Azatarna materialen bidez gizarteen historia ikertzen duen zientzia edo jakintzagaia"
                ],
                "cs": [
                    "Vědní obor zabývající se lidskými kulturami v minulosti"
                ],
                "sl": [
                    "Zgodovinska in antropološka znanost, ki z uporabo materialnih najdb proučuje pretekle družbe"
                ],
                "pl": [
                    "Nauka badająca przeszłości człowieka na podstawie znajdujących się w ziemi, na ziemi lub w wodzie materialnych pozostałości działań ludzkich"
                ],
                "da": [
                    "Viden om menneskets forhistorie"
                ],
                "nl": [
                    "Wetenschap die overblijfselen van oude culturen bestudeert"
                ]
            },
            "related": [
                "http://data.europeana.eu/concept/1924"
            ],
            "exactMatch": [
                "http://www.wikidata.org/entity/Q23498",
                "http://cv.iptc.org/newscodes/subjectcode/01001000",
                "https://d-nb.info/gnd/4002827-6",
                "http://id.loc.gov/authorities/names/sh85006507",
                "http://data.bnf.fr/ark:/12148/cb13318444z",
                "http://id.ndl.go.jp/auth/ndlna/00566298",
                "http://id.nlm.nih.gov/mesh/D001106",
                "http://purl.org/bncf/tid/1064",
                "https://www.freebase.com/m/0h61",
                "https://g.co/kg/m/0h61",
                "http://id.nlm.nih.gov/mesh/I01.076.201.208",
                "http://datos.bne.es/resource/XX525128",
                "http://vocab.getty.edu/aat/300054328",
                "http://id.worldcat.org/fast/812938",
                "http://www.yso.fi/onto/yso/p1265",
                "http://babelnet.org/rdf/s00005391n",
                "http://nlg.okfn.gr/resource/authority/record918",
                "http://zbw.eu/stw/descriptor/19634-6",
                "http://vocabularies.unesco.org/thesaurus/concept298",
                "http://cv.iptc.org/newscodes/mediatopic/20000744",
                "http://uri.gbv.de/terminology/bk/15.15",
                "http://www.yso.fi/onto/ysa/Y94689",
                "http://dbpedia.org/resource/Archaeology"
            ]
        },
        {
            "about": "http://vocab.getty.edu/aat/300188746",
            "prefLabel": {
                "en": [
                    "shipwrecks"
                ],
                "nl": [
                    "schipbreuken"
                ],
                "es": [
                    "naufragios"
                ]
            },
            "altLabel": {
                "en": [
                    "shipwreck",
                    "wrecks (events)"
                ],
                "nl": [
                    "schipbreuk",
                    "scheepsongelukken",
                    "scheepsongeluk"
                ],
                "es": [
                    "naufragio"
                ]
            },
            "note": {
                "en": [
                    "Occasions of the severe damage or loss of a boat or ship at sea."
                ],
                "nl": [
                    "Gevallen van zware beschadiging of het vergaan van een boot of schip op zee."
                ],
                "es": [
                    "Circunstancia de daño severo o pérdida de un bote o barco en el mar."
                ]
            },
            "broader": [
                "http://vocab.getty.edu/aat/300182939"
            ],
            "exactMatch": [
                "http://www.wikidata.org/entity/Q852190"
            ]
        },
        {
            "about": "http://data.europeana.eu/concept/186",
            "prefLabel": {
                "de": [
                    "Schiff"
                ],
                "ru": [
                    "Корабль"
                ],
                "fi": [
                    "Laiva"
                ],
                "pt": [
                    "Navio"
                ],
                "bg": [
                    "Кораб"
                ],
                "lt": [
                    "Laivas"
                ],
                "lv": [
                    "Kuģis"
                ],
                "hr": [
                    "Brod"
                ],
                "fr": [
                    "Navire"
                ],
                "hu": [
                    "Hajó"
                ],
                "sk": [
                    "Loď"
                ],
                "sl": [
                    "Ladja"
                ],
                "ga": [
                    "Long"
                ],
                "ca": [
                    "Vaixell"
                ],
                "sv": [
                    "Fartyg"
                ],
                "el": [
                    "Πλοίο"
                ],
                "en": [
                    "Ship"
                ],
                "it": [
                    "Nave"
                ],
                "es": [
                    "Barco"
                ],
                "et": [
                    "Laev"
                ],
                "eu": [
                    "Barku"
                ],
                "cs": [
                    "Loď"
                ],
                "pl": [
                    "Statek wodny"
                ],
                "ro": [
                    "Navă"
                ],
                "da": [
                    "Skib"
                ],
                "nl": [
                    "Schip"
                ]
            },
            "note": {
                "de": [
                    "Größeres Wasserfahrzeug"
                ],
                "fi": [
                    "Suuri vedessä kulkeva alus"
                ],
                "sv": [
                    "Större flytande vattenfarkost. (Svenska sjölagen definierar fartyg vars skrov har en största längd som överstiger 24 meter som \"skepp\": mindre fartyg definieras som \"båt\".)"
                ],
                "ru": [
                    "Большое судно"
                ],
                "pt": [
                    "Tipo de embarcação"
                ],
                "lt": [
                    "Didelė plaukiojanti transporto priemonė žmonėms ir kroviniams pervežti."
                ],
                "en": [
                    "Large buoyant watercraft"
                ],
                "it": [
                    "Mezzo di trasporto su acqua"
                ],
                "fr": [
                    "Type d'embarcation"
                ],
                "hu": [
                    "Vízi jármű"
                ],
                "es": [
                    "Vehículo con cubierta para navegaciones marítimas"
                ],
                "et": [
                    "Suur veesõiduk"
                ],
                "eu": [
                    "Itsasontzi mota"
                ],
                "cs": [
                    "Větší plavidlo"
                ],
                "sk": [
                    "Druh dopravného prostriedku dopravujúceho po vode"
                ],
                "ga": [
                    "Árthach mór"
                ],
                "pl": [
                    "Duży pojazd wodny"
                ],
                "ro": [
                    "Ambarcațiune plutitoare mare"
                ],
                "da": [
                    "Større fartøj"
                ],
                "ca": [
                    "Vehicle amb coberta per navegacions marítimes"
                ],
                "nl": [
                    "Transportmiddel over water"
                ]
            },
            "exactMatch": [
                "http://www.wikidata.org/entity/Q11446",
                "http://live.dbpedia.org/ontology/Ship",
                "http://rdf.muninn-project.org/ontologies/naval#Ship",
                "https://d-nb.info/gnd/4052385-8",
                "http://id.loc.gov/authorities/names/sh85121591",
                "http://id.ndl.go.jp/auth/ndlna/00570714",
                "http://id.nlm.nih.gov/mesh/D012767",
                "http://purl.org/bncf/tid/2017",
                "https://www.freebase.com/m/06q74",
                "https://g.co/kg/m/06q74",
                "http://id.nlm.nih.gov/mesh/J01.937.817",
                "http://vocab.getty.edu/aat/300082981",
                "http://iconclass.org/46C21",
                "http://www.yso.fi/onto/yso/p4911",
                "http://babelnet.org/rdf/s00071103n",
                "http://zbw.eu/stw/descriptor/14455-3",
                "http://vocabularies.unesco.org/thesaurus/concept4445",
                "http://vocabularies.unesco.org/thesaurus/concept13218",
                "http://dbpedia.org/resource/Ship"
            ]
        },
        {
            "about": "http://data.europeana.eu/concept/26",
            "prefLabel": {
                "de": [
                    "Artefakt"
                ],
                "fi": [
                    "Artefakti"
                ],
                "ru": [
                    "Артефакт"
                ],
                "pt": [
                    "Artefato"
                ],
                "bg": [
                    "Артефакт"
                ],
                "lt": [
                    "Archeologinis radinys"
                ],
                "lv": [
                    "Arheoloģisks artefakts"
                ],
                "hr": [
                    "Artefakt"
                ],
                "fr": [
                    "Artefact archéologique"
                ],
                "hu": [
                    "Megmunkált tárgy"
                ],
                "sk": [
                    "Artefakt"
                ],
                "sl": [
                    "Arheološki artefakt"
                ],
                "ga": [
                    "Déantán seandálaíochta"
                ],
                "ca": [
                    "Objecte arqueològic"
                ],
                "sv": [
                    "Artefakt"
                ],
                "el": [
                    "Τέχνεργο"
                ],
                "en": [
                    "Archaeological artefact"
                ],
                "it": [
                    "Manufatto"
                ],
                "es": [
                    "Artefacto arqueológico"
                ],
                "et": [
                    "Artefakt"
                ],
                "eu": [
                    "Artefaktu arkeologiko"
                ],
                "cs": [
                    "Artefakt"
                ],
                "pl": [
                    "Artefakt archeologiczny"
                ],
                "ro": [
                    "Artefact"
                ],
                "da": [
                    "Artefakt"
                ],
                "nl": [
                    "Artefact"
                ]
            },
            "note": {
                "de": [
                    "Von Menschen hergestellter Gegenstand, archäologischer Begriff"
                ],
                "fi": [
                    "Keinotekoinen esine"
                ],
                "sv": [
                    "Föremål av arkeologiskt intresse tillverkat av människor"
                ],
                "ru": [
                    "Рукотворная археологическая находка"
                ],
                "pt": [
                    "Algo feito por humanos e de interesse arqueológico"
                ],
                "el": [
                    "Πηγή αρχαιολογικής μαρτυρίας"
                ],
                "en": [
                    "Something made or modified by humans and of archaeological interest"
                ],
                "it": [
                    "Oggetto la cui forma è giustificata dalla prestazione a cui era destinato"
                ],
                "fr": [
                    "Vestige façonné par l'homme et d'intérêt archéologique"
                ],
                "hu": [
                    "Régészetileg jelentős, ember alkotta tárgy"
                ],
                "es": [
                    "Material u objeto distintivo que se encuentra en una excavación arqueológica"
                ],
                "eu": [
                    "Gizakiak egindako eta arkeologiarako interesa duen objektua"
                ],
                "sl": [
                    "Nekaj, kar so naredili ali spremenili ljudje in je zanimivo za arheologijo"
                ],
                "pl": [
                    "Każdy przedmiot wykonany lub zmodyfikowany przez człowieka, a odkryty przez archeologów"
                ],
                "ro": [
                    "Obiect arheologic găsit care a fost confecționat de oameni"
                ],
                "da": [
                    "Menneskeskabt objekt af arkæologisk interesse"
                ],
                "nl": [
                    "Gevonden voorwerp, gemaakt/gebruikt door mensen, tijdens een archeologische opgraving"
                ]
            },
            "exactMatch": [
                "http://www.wikidata.org/entity/Q220659",
                "https://d-nb.info/gnd/4143114-5",
                "http://purl.org/bncf/tid/2678",
                "https://www.freebase.com/m/02skpt",
                "https://g.co/kg/m/02skpt",
                "http://vocab.getty.edu/aat/300117127",
                "http://vocab.getty.edu/aat/300234110",
                "http://babelnet.org/rdf/s00005956n",
                "http://g.co/kg/g/120hzgr2",
                "http://vocabularies.unesco.org/thesaurus/concept2527",
                "http://dbpedia.org/resource/Artifact_(archaeology)"
            ]
        },
        {
            "about": "http://data.europeana.eu/concept/1816",
            "prefLabel": {
                "de": [
                    "Holz"
                ],
                "fi": [
                    "Puuaines"
                ],
                "ru": [
                    "Древесина"
                ],
                "pt": [
                    "Madeira"
                ],
                "bg": [
                    "Дървесина"
                ],
                "lt": [
                    "Mediena"
                ],
                "hr": [
                    "Drvo"
                ],
                "lv": [
                    "Koksne"
                ],
                "fr": [
                    "Bois"
                ],
                "hu": [
                    "fa"
                ],
                "sk": [
                    "Drevo"
                ],
                "sl": [
                    "Les"
                ],
                "ga": [
                    "Adhmad"
                ],
                "ca": [
                    "Fusta"
                ],
                "sv": [
                    "Trä"
                ],
                "el": [
                    "Ξύλο"
                ],
                "mt": [
                    "Injam"
                ],
                "en": [
                    "Wood"
                ],
                "it": [
                    "Legno"
                ],
                "es": [
                    "Madera"
                ],
                "et": [
                    "Puit"
                ],
                "cs": [
                    "Dřevo"
                ],
                "eu": [
                    "Zur"
                ],
                "pl": [
                    "Drewno"
                ],
                "da": [
                    "Træ"
                ],
                "ro": [
                    "Lemn"
                ],
                "nl": [
                    "Hout"
                ]
            },
            "note": {
                "de": [
                    "Faseriges Material von Bäumen oder anderen Pflanzen"
                ],
                "sv": [
                    "Material som fås vid avverkning och bearbetning av träd"
                ],
                "fi": [
                    "Monissa puissa olevaa kovaa solukkoa"
                ],
                "ru": [
                    "Внутренняя часть дерева"
                ],
                "pt": [
                    "Material duro, fibroso obtido das árvores"
                ],
                "el": [
                    "Φυσικό και ανανεώσιμο υλικό"
                ],
                "en": [
                    "Fibrous material from trees or other plants"
                ],
                "it": [
                    "Materiale ricavato dai fusti delle piante"
                ],
                "fr": [
                    "Matériau naturel issu d'arbres ou de plantes ligneuses"
                ],
                "hu": [
                    "Fás növények szárának farészeiből nyert kemény, rostos anyag"
                ],
                "es": [
                    "Material duro y fibroso obtenido de los árboles u otras plantas, que se emplea para fines como mobiliario, utensilios, instrumentos, objetos, etc."
                ],
                "eu": [
                    "Egurra, enborren materiala"
                ],
                "cs": [
                    "Materiál tvořený pevnou pletivovou tkání stromů a jiných dřevin"
                ],
                "sl": [
                    "Organski material, ki ga pridobivamo iz dreves in grmov"
                ],
                "ga": [
                    "Ábhar déanta de chrainn nó de phlandaí eile"
                ],
                "pl": [
                    "Surowiec z drzew"
                ],
                "ro": [
                    "Material obținut din arbori și alte plante"
                ],
                "da": [
                    "Materiale"
                ],
                "ca": [
                    "Material dur i fibrós obtingut dels arbres i altres plantes llenyoses"
                ],
                "nl": [
                    "Materiaal afkomstig van bomen"
                ]
            },
            "broader": [
                "http://data.europeana.eu/concept/2099"
            ],
            "exactMatch": [
                "http://www.wikidata.org/entity/Q287",
                "http://purl.obolibrary.org/obo/ENVO_00002040",
                "https://d-nb.info/gnd/4025668-6",
                "http://id.loc.gov/authorities/names/sh85147783",
                "http://data.bnf.fr/ark:/12148/cb11976008h",
                "http://id.ndl.go.jp/auth/ndlna/00567803",
                "http://id.nlm.nih.gov/mesh/D014934",
                "http://purl.org/bncf/tid/3389",
                "https://www.freebase.com/m/083vt",
                "https://g.co/kg/m/083vt",
                "http://id.nlm.nih.gov/mesh/A18.450.500.500",
                "http://id.nlm.nih.gov/mesh/J01.637.241.900",
                "http://vocab.getty.edu/aat/300011914",
                "http://iconclass.org/47G543",
                "http://www.yso.fi/onto/yso/p16542",
                "http://babelnet.org/rdf/s00081492n",
                "http://thesaurus.europeanafashion.eu/thesaurus/10577",
                "http://zbw.eu/stw/descriptor/14150-4",
                "http://vocabularies.unesco.org/thesaurus/concept4159",
                "http://dbpedia.org/resource/Wood"
            ]
        },
        {
            "about": "http://vocab.getty.edu/aat/300198466",
            "prefLabel": {
                "de": [
                    "Butterfass (Behälter)"
                ],
                "en": [
                    "butter tubs"
                ],
                "fr": [
                    "seau à beurre"
                ],
                "nl": [
                    "botervaten"
                ]
            },
            "altLabel": {
                "de": [
                    "Butterfässer (Behälter)"
                ],
                "en": [
                    "butter tub",
                    "tub, butter",
                    "tubs, butter",
                    "cubas de mantequilla"
                ],
                "nl": [
                    "botervat"
                ],
                "es": [
                    "cuba de mantequilla"
                ]
            },
            "note": {
                "de": [
                    "Hölzernes Daubenfass mit fest schließendem Deckel zum Bevorraten oder Verkaufen von Butter."
                ],
                "en": [
                    "Wooden staved tubs with close-fitting tops used for butter storage or sale."
                ],
                "nl": [
                    "Houten kuipen van duigen met nauwsluitende bovenkanten, gebruikt om boter in op te slaan of te verkopen."
                ],
                "es": [
                    "Cubas de madera con duelas y cubiertas ajustadas, usadas para almacenar o vender mantequilla."
                ]
            },
            "broader": [
                "http://vocab.getty.edu/aat/300197577"
            ]
        }
    ],
    "edmDatasetName": [
        "181_Share3D_181"
    ],
    "europeanaAggregation": {
        "about": "/aggregation/europeana/181/share3d_2327",
        "aggregatedCHO": "/item/181/share3d_2327",
        "edmCountry": {
            "def": [
                "Netherlands"
            ]
        },
        "edmLanguage": {
            "def": [
                "en"
            ]
        },
        "edmPreview": "https://api.europeana.eu/thumbnail/v2/url.json?uri=https%3A%2F%2Fmedia.sketchfab.com%2Fmodels%2Fb135c38a0a1e414784c6db4469501bfd%2Fthumbnails%2F46674cf7bd584c8996a59fe229b1484d%2F8e3bb9c22fb3434fb8e2f33e233ec7e0.jpeg&type=3D",
        "edmLandingPage": "https://www.europeana.eu/item/181/share3d_2327",
        "dqvHasQualityAnnotation": [
            {
                "created": "2025-12-08T13:57:26.048214779Z",
                "target": [
                    "/aggregation/europeana/181/share3d_2327"
                ],
                "body": "http://www.europeana.eu/schemas/epf/contentTier4"
            },
            {
                "created": "2025-12-08T13:57:26.048222624Z",
                "target": [
                    "/aggregation/europeana/181/share3d_2327"
                ],
                "body": "http://www.europeana.eu/schemas/epf/metadataTierC"
            }
        ]
    },
    "europeanaCollectionName": [
        "181_Share3D_181"
    ],
    "europeanaCompleteness": 10,
    "organizations": [
        {
            "about": "http://data.europeana.eu/organization/5392",
            "prefLabel": {
                "nl": [
                    "Huis van Hilde"
                ]
            }
        },
        {
            "about": "http://data.europeana.eu/organization/1617",
            "prefLabel": {
                "en": [
                    "CARARE"
                ]
            }
        }
    ],
    "places": [
        {
            "about": "#edmPlace_share3d:2327/SP.1",
            "prefLabel": {
                "def": [
                    "Burgzand Noord; BZN17 | Palmhoutwrak, Waddenzee, Texel"
                ]
            },
            "latitude": 53.0483,
            "longitude": 4.9374
        }
    ],
    "providedCHOs": [
        {
            "about": "/item/181/share3d_2327"
        }
    ],
    "proxies": [
        {
            "about": "/proxy/europeana/181/share3d_2327",
            "dcIdentifier": {
                "def": [
                    "share3d:2327"
                ]
            },
            "dcTitle": {
                "def": [
                    "This title"
                ]
            },
            "dcLanguage": {
                "def": [
                    "en"
                ]
            },
            "dcSubject": {
                "def": [
                    "http://data.europeana.eu/concept/80",
                    "http://data.europeana.eu/concept/1816",
                    "http://data.europeana.eu/concept/26",
                    "http://data.europeana.eu/concept/186"
                ]
            },
            "dctermsCreated": {
                "def": [
                    "#2025"
                ]
            },
            "dctermsTemporal": {
                "def": [
                    "#1650%7E"
                ]
            },
            "dcTermsMedium": {
                "def": [
                    "http://data.europeana.eu/concept/1766"
                ]
            },
            "proxyIn": [
                "/aggregation/europeana/181/share3d_2327"
            ],
            "proxyFor": "/item/181/share3d_2327",
            "lineage": [
                "/proxy/provider/181/share3d_2327"
            ],
            "year": {
                "def": [
                    "2025"
                ]
            },
            "europeanaProxy": True
        },
        {
            "about": "/proxy/provider/181/share3d_2327",
            "dcCreator": {
                "def": [
                    "Archeologiemuseum Huis van Hilde, Kees Zwaan",
                    "http://viaf.org/viaf/283149196489174791761",
                    "http://viaf.org/viaf/305323279",
                    "http://viaf.org/viaf/710155284789387061477",
                    "http://viaf.org/viaf/103146284513115332755",
                    "http://viaf.org/viaf/313539601"
                ]
            },
            "dcDescription": {
                "en": [
                    "Butter churn made from ten staves of pine wood (Pinus sp.) and a base of silver fir wood (Abies alba). Found in the shipwreck BZN17 (Palmwood Wreck) in the Wadden Sea near Texel.\nMeasurements (cm): 14.3/11.2/-\nCollection Archeologiemuseum Huis van Hilde PNH 6284-419"
                ],
                "nl": [
                    "Botervat gemaakt uit tien duigen van dennenhout (Pinus Sp.) en een bodem uit het hout van een zilverspar (Abies alba). Gevonden in het scheepswrak BZN17 (Palmhoutwrak) in de Waddenzee bij Texel.\nAfmetingen (cm): 14,3/11,2/-\nCollectie Archeologiemuseum Huis van Hilde  PNH 6284-419"
                ]
            },
            "dcFormat": {
                "en": [
                    "glTF"
                ]
            },
            "dcIdentifier": {
                "def": [
                    "share3d:2327"
                ]
            },
            "dcLanguage": {
                "def": [
                    "English"
                ]
            },
            "dcRelation": {
                "def": [
                    "https://hdl.handle.net/21.12153/obj61312",
                    "https://hdl.handle.net/21.12153/sit2046"
                ]
            },
            "dcSubject": {
                "def": [
                    "http://vocab.getty.edu/aat/300082981",
                    "http://vocab.getty.edu/aat/300188746",
                    "http://vocab.getty.edu/aat/300234110",
                    "http://vocab.getty.edu/aat/300198466",
                    "http://vocab.getty.edu/aat/300387535"
                ],
                "nl": [
                    "burgzand-noord",
                    "churn",
                    "17thcentury",
                    "noord-holland",
                    "den",
                    "maritimearchaeology",
                    "maritime-archaeology",
                    "household-item",
                    "householdobjects",
                    "botervat",
                    "excavation-archaeological",
                    "texel-archeologie",
                    "waddensea",
                    "shipwreck-archaeology-photogrammetry",
                    "hout",
                    "dennehout",
                    "abies",
                    "shipwreck",
                    "museumcollection",
                    "archaeology",
                    "maritieme-collectie",
                    "texel",
                    "museumsonsketchfab",
                    "Cultural Heritage & History",
                    "wood",
                    "modern-age",
                    "Food & Drink",
                    "Archeologie",
                    "archaeology-3dmodel",
                    "bzn17",
                    "zilverspar",
                    "17th-century",
                    "wooden",
                    "abies_alba",
                    "pinus",
                    "shipwreck-archaeology",
                    "boter",
                    "waddenzee",
                    "huis-van-hilde",
                    "6284-419",
                    "churn-butter"
                ]
            },
            "dcTitle": {
                "en": [
                    "Butter churn (ca. 1650)"
                ],
                "nl": [
                    "Botervat (ca. 1650)"
                ]
            },
            "dcType": {
                "en": [
                    "3D"
                ]
            },
            "dctermsCreated": {
                "def": [
                    "2025"
                ]
            },
            "dctermsIsPartOf": {
                "en": [
                    "Share3D",
                    "Netherlands"
                ]
            },
            "dctermsProvenance": {
                "nl": [
                    "Made with 3DF Zephyr photogrammetry software.; Photogrammetry"
                ]
            },
            "dctermsSpatial": {
                "def": [
                    "#edmPlace_share3d:2327/SP.1"
                ]
            },
            "dctermsTemporal": {
                "def": [
                    "share3d:2327/TMP.1",
                    "share3d:2327/TMP.2"
                ],
                "nl": [
                    "ca. 1650"
                ]
            },
            "proxyIn": [
                "/aggregation/provider/181/share3d_2327"
            ],
            "proxyFor": "/item/181/share3d_2327",
            "edmType": "3D",
            "europeanaProxy": False
        }
    ],
    "timespans": [
        {
            "about": "#2025",
            "prefLabel": {
                "zxx": [
                    "2025"
                ]
            },
            "begin": {
                "def": [
                    "2025-01-01"
                ]
            },
            "end": {
                "def": [
                    "2025-12-31"
                ]
            },
            "isPartOf": {
                "def": [
                    "http://data.europeana.eu/timespan/21"
                ]
            },
            "skosNotation": {
                "def": [
                    "2025"
                ]
            }
        },
        {
            "about": "#1650%7E",
            "prefLabel": {
                "zxx": [
                    "1650~"
                ]
            },
            "note": {
                "def": [
                    "approximate"
                ]
            },
            "begin": {
                "def": [
                    "1650-01-01"
                ]
            },
            "end": {
                "def": [
                    "1650-12-31"
                ]
            },
            "isPartOf": {
                "def": [
                    "http://data.europeana.eu/timespan/17"
                ]
            },
            "skosNotation": {
                "def": [
                    "1650~"
                ]
            }
        },
        {
            "about": "share3d:2327/TMP.1",
            "prefLabel": {
                "en": [
                    "17th century CE"
                ]
            },
            "begin": {
                "def": [
                    "1600"
                ]
            },
            "end": {
                "def": [
                    "1699"
                ]
            },
            "owlSameAs": [
                "http://vocab.getty.edu/page/aat/300404511",
                "https://www.wikidata.org/wiki/Q7016"
            ]
        },
        {
            "about": "share3d:2327/TMP.2",
            "prefLabel": {
                "en": [
                    "Modern"
                ]
            },
            "begin": {
                "def": [
                    "1890"
                ]
            },
            "end": {
                "def": [
                    "1979"
                ]
            },
            "owlSameAs": [
                "http://vocab.getty.edu/page/aat/300264736"
            ]
        },
        {
            "about": "http://data.europeana.eu/timespan/17",
            "prefLabel": {
                "de": [
                    "17. Jahrhundert"
                ],
                "fi": [
                    "1600-luku"
                ],
                "ru": [
                    "XVII век"
                ],
                "pt": [
                    "Século XVII"
                ],
                "bg": [
                    "17 век"
                ],
                "lt": [
                    "XVII amžius"
                ],
                "hr": [
                    "17. stoljeće"
                ],
                "lv": [
                    "17. gadsimts"
                ],
                "fr": [
                    "XVIIe siècle"
                ],
                "hu": [
                    "17. század"
                ],
                "sk": [
                    "17. storočie"
                ],
                "sl": [
                    "17. stoletje"
                ],
                "ga": [
                    "17ú haois"
                ],
                "ca": [
                    "Segle XVII"
                ],
                "sv": [
                    "1600-talet"
                ],
                "el": [
                    "17ος αιώνας"
                ],
                "mt": [
                    "Seklu XVII"
                ],
                "en": [
                    "17th century"
                ],
                "it": [
                    "XVII secolo"
                ],
                "es": [
                    "Siglo XVII"
                ],
                "et": [
                    "17. sajand"
                ],
                "cs": [
                    "17. století"
                ],
                "eu": [
                    "XVII. mendea"
                ],
                "pl": [
                    "XVII wiek"
                ],
                "da": [
                    "17. århundrede"
                ],
                "ro": [
                    "Secolul al XVII-lea"
                ],
                "nl": [
                    "17e eeuw"
                ]
            },
            "altLabel": {
                "sv": [
                    "1600-tal",
                    "17:e århundradet",
                    "17:e seklet",
                    "1600-talet (århundrade)",
                    "1600-talet (sekel)"
                ],
                "ru": [
                    "17 век"
                ],
                "mt": [
                    "Seklu 17"
                ],
                "en": [
                    "17th-century",
                    "History, 17th century",
                    "Seventeenth century"
                ],
                "it": [
                    "Seicento",
                    "17° secolo",
                    "Secolo XVII",
                    "XVII Secolo",
                    "Diciassettesimo secolo",
                    "'600",
                    "17º secolo"
                ],
                "fr": [
                    "17e siècle"
                ],
                "nl": [
                    "Zeventiende eeuw"
                ]
            },
            "begin": {
                "def": [
                    "1601-01-01"
                ]
            },
            "end": {
                "def": [
                    "1700-12-31"
                ]
            },
            "owlSameAs": [
                "http://www.wikidata.org/entity/Q7016",
                "http://id.loc.gov/authorities/names/sh85120427",
                "http://data.bnf.fr/ark:/12148/cb120419182",
                "http://data.bnf.fr/ark:/12148/cb11975998j",
                "http://id.nlm.nih.gov/mesh/D049670",
                "https://www.freebase.com/m/08b2m",
                "https://g.co/kg/m/08b2m",
                "http://id.nlm.nih.gov/mesh/K01.400.504.750",
                "http://vocab.getty.edu/aat/300404511",
                "http://id.worldcat.org/fast/1113663",
                "http://babelnet.org/rdf/s02814624n",
                "http://dbpedia.org/resource/17th_century"
            ]
        },
        {
            "about": "http://data.europeana.eu/timespan/21",
            "prefLabel": {
                "de": [
                    "21. Jahrhundert"
                ],
                "fi": [
                    "2000-luku"
                ],
                "ru": [
                    "XXI век"
                ],
                "pt": [
                    "Século XXI"
                ],
                "bg": [
                    "21 век"
                ],
                "lt": [
                    "XXI amžius"
                ],
                "hr": [
                    "21. stoljeće"
                ],
                "lv": [
                    "21. gadsimts"
                ],
                "fr": [
                    "XXIe siècle"
                ],
                "hu": [
                    "21. század"
                ],
                "sk": [
                    "21. storočie"
                ],
                "sl": [
                    "21. stoletje"
                ],
                "ga": [
                    "21ú haois"
                ],
                "ca": [
                    "Segle XXI"
                ],
                "sv": [
                    "2000-talet"
                ],
                "el": [
                    "21ος αιώνας"
                ],
                "en": [
                    "21st century"
                ],
                "it": [
                    "XXI secolo"
                ],
                "es": [
                    "Siglo XXI"
                ],
                "et": [
                    "21. sajand"
                ],
                "cs": [
                    "21. století"
                ],
                "eu": [
                    "XXI. mendea"
                ],
                "pl": [
                    "XXI wiek"
                ],
                "da": [
                    "21. århundrede"
                ],
                "ro": [
                    "Secolul al XXI-lea"
                ],
                "nl": [
                    "21e eeuw"
                ]
            },
            "altLabel": {
                "de": [
                    "21. Jh.",
                    "21. Jhd.",
                    "21. Jhdt.",
                    "21. Jhrh.",
                    "21. Jahrh.",
                    "21. Zentennium",
                    "21. Centennium",
                    "21. Hektode"
                ],
                "sv": [
                    "21:a århundradet",
                    "21:a seklet",
                    "2000-tal",
                    "2000-talet (århundrade)",
                    "2000-talet (sekel)"
                ],
                "fi": [
                    "21. vuosisata"
                ],
                "ru": [
                    "21 век"
                ],
                "bg": [
                    "XXI век",
                    "21. век"
                ],
                "en": [
                    "21st-century",
                    "Twenty-first century",
                    "History, 21st Century",
                    "XXI Century"
                ],
                "it": [
                    "21° secolo",
                    "Secolo XXI",
                    "Ventunesimo secolo",
                    "XXI Secolo",
                    "Duemila"
                ],
                "fr": [
                    "21e siècle",
                    "Vingt et unième siècle",
                    "21ème siècle"
                ],
                "es": [
                    "Historia, siglo 21",
                    "Siglo 21",
                    "Este siglo",
                    "Siglo veintiuno"
                ],
                "pl": [
                    "21 wiek",
                    "21 stulecie",
                    "XXI stulecie",
                    "XXI w"
                ],
                "ro": [
                    "Secolul 21",
                    "Secolul douăzeci și unu",
                    "Secoulul XXI"
                ],
                "nl": [
                    "Eenentwintigste eeuw"
                ],
                "ca": [
                    "Segle 21"
                ]
            },
            "begin": {
                "def": [
                    "2001-01-01"
                ]
            },
            "end": {
                "def": [
                    "2100-12-31"
                ]
            },
            "owlSameAs": [
                "http://www.wikidata.org/entity/Q6939",
                "http://data.culture.fr/thesaurus/resource/ark:/67717/T4-46",
                "http://id.loc.gov/authorities/names/sh85139024",
                "http://id.loc.gov/authorities/names/sh2002012478",
                "http://data.bnf.fr/ark:/12148/cb11930812p",
                "http://id.nlm.nih.gov/mesh/D049674",
                "https://www.freebase.com/m/08b43",
                "https://g.co/kg/m/08b43",
                "http://id.nlm.nih.gov/mesh/K01.400.504.984",
                "http://vocab.getty.edu/aat/300404515",
                "http://id.worldcat.org/fast/1159816",
                "http://babelnet.org/rdf/s01157225n",
                "http://dbpedia.org/resource/21st_century"
            ]
        }
    ],
    "timestamp_created": "2025-12-08T13:57:21.616Z",
    "timestamp_created_epoch": 1765202241616,
    "timestamp_update": "2025-12-08T13:57:21.616Z",
    "timestamp_update_epoch": 1765202241616,
    "type": "3D"
}]

    source = Source.EUROPEANA

    transformed_data = transformer.transform(source, file_content)
    for data in transformed_data:
        print(data.created_by)