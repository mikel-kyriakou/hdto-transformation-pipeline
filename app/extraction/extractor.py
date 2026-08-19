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
        print(f"Extracting path: {path} with strategy: {strategy}")
        if path is None:
            return None

        parts = path.split(".")
        result = self._extract(record, parts)

        print(f"Extracted result before strategy: {result}")

        match strategy:
            case "extract_first":
                if isinstance(result, list):
                    return result[0] if result else None
                
            case "map_language":
                if isinstance(result, dict):
                    return self._map_language(result)
                elif isinstance(result, list):
                    return [self._map_language(item) for item in result]

            case "map_language_list":
                if isinstance(result, dict):
                    result = self._map_language(result)
                elif isinstance(result, list):
                    result = [self._map_language(item) for item in result]

                if isinstance(result, list):
                    return next((item for item in result if item is not None), None)

                return result
                

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

    def _map_language(self, value: dict) -> list | str | None:

        print(f"Step 1: {value}")
        if not isinstance(value, dict):
            return value

        print(f"Step 2: {value}")

        if "def" in value:
            value = value["def"]
        elif "en" in value:
            value = value["en"]
        else:
            value = next(iter(value.values()), None)

        print(f"Step 3: {value}")

        if isinstance(value, list):
            return value[0] if len(value) > 0 else None

        print(f"Step 4: {value}")

        return value