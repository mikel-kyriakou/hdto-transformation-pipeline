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

        match strategy:
            case "extract_first":
                if isinstance(result, list):
                    return result[0] if result else None
                
            case "map_language":
                if isinstance(result, dict):
                    return self._map_language(result)
                elif isinstance(result, list):
                    return [self._map_language(item) for item in result if item is not None]

            case "map_language_extract_first":
                if isinstance(result, dict):
                    result = self._map_language(result)
                elif isinstance(result, list):
                    result = [self._map_language(item) for item in result]

                if isinstance(result, list):
                    return next((item for item in result if item is not None), None)

                return result

            case "add_europeana_base_url":
                if not isinstance(result, str):
                    return None

                return f"https://www.europeana.eu/item{result}"

            case "resolve_concept":
                if not isinstance(result, list):
                    result = [result]

                values = [] 
                for val in result:
                    if not isinstance(val, dict):
                        continue

                    concept_uri = self._map_language(val)

                    concepts_list = record.get("concepts", [])
                    for concept in concepts_list:
                        if "about" in concept and concept["about"] == concept_uri:
                            values.append(self._map_language(concept.get("prefLabel", {})))

                return values

            case "map_language_extract_first_remove_hashtag":
                if isinstance(result, dict):
                    result = self._map_language(result)
                elif isinstance(result, list):
                    result = [self._map_language(item) for item in result]

                if isinstance(result, list):
                    item = next((item for item in result if item is not None), None)
                    if isinstance(item, str) and item.startswith("#"):
                        return item[1:]

                return None

            case "resolve_place_name":
                if not isinstance(result, list):
                    return None
                result = [elem for elem in result if elem]

                about_raw = result[0]
                about = self._map_language(about_raw)
                if not about:
                    return None

                place = self._extract_europeana_place(record, about)

                if place is None or 'prefLabel' not in place:
                    return None

                return self._map_language(place['prefLabel'])

            case "resolve_place_lat":
                if not isinstance(result, list):
                    return None
                result = [elem for elem in result if elem]

                about_raw = result[0]
                about = self._map_language(about_raw)
                if not about:
                    return None

                place = self._extract_europeana_place(record, about)

                return place.get('latitude') if place else None

            case "resolve_place_long":
                if not isinstance(result, list):
                    return None
                result = [elem for elem in result if elem]

                about_raw = result[0]
                about = self._map_language(about_raw)
                if not about:
                    return None

                place = self._extract_europeana_place(record, about)

                return place.get('longitude') if place else None

            case "resolve_europeana_creator_id":
                if not isinstance(result, list):
                    result=[result]

                values = []
                for r in result:
                    if not isinstance(r, dict):
                        continue

                    to_add = self._map_language(r, as_list=True)
                    if to_add is None:
                        continue
                    values.extend(to_add)

                return [val if val.startswith('http') else None for val in values]

            case "resolve_europeana_creator_name":
                if not isinstance(result, list):
                    result=[result]

                values = []
                for r in result:
                    if not isinstance(r, dict):
                        continue

                    to_add = self._map_language(r, as_list=True)
                    if to_add is None:
                        continue
                    values.extend(to_add)

                return [val if not val.startswith('http') else None for val in values]



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

    def _map_language(self, value: dict, as_list: bool = False) -> list[str] | str | None:
        if not isinstance(value, dict):
            return value

        if "def" in value:
            value = value["def"]
        elif "en" in value:
            value = value["en"]
        else:
            value = next(iter(value.values()), None)

        if isinstance(value, list):
            if as_list:
                return value
            return value[0] if len(value) > 0 else None

        return value

    def _extract_europeana_place(self, record: dict, about: str) -> dict | None:
        if 'places' not in record:
            return None

        places = record['places']
        for place in places:
            if 'about' in place and place['about'] == about:
                return place

        return None