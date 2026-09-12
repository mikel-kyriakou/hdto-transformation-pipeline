import json

from fastapi import UploadFile


class FileReader:
    
    @staticmethod
    async def read_file(file: UploadFile) -> list | dict:
        file_content_raw = await file.read()
        try:
            content = json.loads(file_content_raw)
            if not isinstance(content, list):
                return [content]
            return content
        except json.JSONDecodeError:
            return {"error": "Invalid JSON file."}