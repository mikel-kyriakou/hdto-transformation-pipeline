from typing import Protocol

from models.enums import Source


class SourceIdentifierProtocol(Protocol):

    def execute(self, file_content: dict) -> Source:
        ...