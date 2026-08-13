import yaml
from pathlib import Path

from app.models.enums import Source


class RulesLoader:

    REQUIREMENTS_DIR = Path(__file__).parent / 'rules_definitions'

    SOURCE_FILES = {
        Source.CUSTOM: "custom.yaml",
        Source.EUROPEANA: "europeana.yaml",
        Source.DPLA: "dpla.yaml"
    }
    
    def load(self, source: Source) -> dict:
        file = f"{self.REQUIREMENTS_DIR}/{self.SOURCE_FILES[source]}"

        with open(file, 'r') as f:
            config = yaml.safe_load(f)

            return config

    def load_requirements(self, source: Source) -> list[str]:
        return self.load(source)['FIELDS']['REQUIRED']

    def load_mapping_rules(self, source: Source) -> dict:
        return self.load(source)['MAPPING']


if __name__ == "__main__":
    loader = RulesLoader()
    # print(loader.load_requirements(Source.CUSTOM))
    print(loader.load_mapping_rules(Source.CUSTOM))
