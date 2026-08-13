class Extractor:
    """
    Extracts values from nested metadata dictionaries using dot-separated paths.
    
    Supports traversing nested objects and lists using the [] notation.
    For example:
        - "creator.name" extracts a nested field
        - "proxies[].dcTitle.en[]" extracts values from lists
    
    Returns None if the path does not exist or if the value is not found.
    """

    def extract(self, record: dict, path: str | None, strategy: str | None = None) -> str | list | None:
        if path is None:
            return None

        parts = path.split(".")
        result = self._extract(record, parts)

        if strategy == "extract_first" and isinstance(result, list):
            return result[0] if result else None

        return result

    def _extract(self, value, parts) -> str | list | None:

        if not parts:
            return value

        part = parts[0]

        if part.endswith("[]"):
            key = part[:-2]

            if not isinstance(value, dict):
                return None

            if key not in value:
                return None

            values = value[key]

            if not isinstance(values, list):
                return None

            result = [
                self._extract(item, parts[1:])
                for item in values
            ]

            return result if len(result) > 0 else None

        if not isinstance(value, dict):
            return None

        if part not in value:
            return None

        return self._extract(value[part], parts[1:])