from enum import StrEnum


class Source(StrEnum):
    EUROPEANA = "Europeana"
    DPLA = "DPLA"
    CUSTOM = "Custom"

class OutputFormat(StrEnum):
    TTL = "turtle"
    XML = "xml"