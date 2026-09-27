from enum import StrEnum


class Source(StrEnum):
    EUROPEANA = "Europeana"
    DPLA = "DPLA"
    CUSTOM = "Custom"

class OutputFormat(StrEnum):
    TTL = "turtle"
    XML = "xml"

    @property
    def media_type(self) -> "MediaType":
        return MediaType[self.name]


class MediaType(StrEnum):
    TTL = "text/turtle"
    XML = "application/rdf+xml"