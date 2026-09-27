from pydantic import ValidationError

from app.models.enums import Source
from app.models.models import CustomMetadata


class IdentifySourceService:

    def identify_source(self, file_content: list) -> Source:

        if all(self._is_europeana_item(item) for item in file_content):
            return Source.EUROPEANA
        elif all(self._is_dpla_item(item) for item in file_content):
            return Source.DPLA
        elif all(self._is_custom_item(item) for item in file_content):
            return Source.CUSTOM
        else:
            raise ValueError("Source not supported")

    def _is_europeana_item(self, file_content: dict) -> bool:
        if "europeanaAggregation" not in file_content:
            return False

        europeana_aggregation = file_content["europeanaAggregation"]
        if "about" not in europeana_aggregation:
            return False

        about = europeana_aggregation["about"]
        return about.startswith("/aggregation/europeana/")
            
    def _is_dpla_item(self, file_content: dict) -> bool:
        if "@context" not in file_content:
            return False
        
        context = file_content["@context"]
        return context == "http://dp.la/api/items/context"
    
    def _is_custom_item(self, file_content: dict) -> bool:
        try:
            CustomMetadata.model_validate(file_content)
            return True
        except ValidationError:
            return False    
    
def load_identify_source_service() -> IdentifySourceService:
    return IdentifySourceService()