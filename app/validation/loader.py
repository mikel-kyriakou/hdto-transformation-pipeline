import yaml
from pathlib import Path

from app.models.enums import Source


class RequirementsLoader:

    REQUIREMENTS_DIR = Path(__file__).parent / 'requirements'

    SOURCE_FILES = {
        Source.CUSTOM: "custom.yaml",
        Source.EUROPEANA: "europeana.yaml",
        Source.DPLA: "dpla.yaml"
    }
    
    def load(self, source: Source) -> list[str]:
        file = f"{self.REQUIREMENTS_DIR}/{self.SOURCE_FILES[source]}"

        with open(file, 'r') as f:
            config = yaml.safe_load(f)

            return config['FIELDS']['REQUIRED']
