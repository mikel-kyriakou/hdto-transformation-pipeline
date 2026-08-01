import json

from fastapi import UploadFile


class FileReader:
    
    @staticmethod
    async def read_file(file: UploadFile) -> dict:
        file_content_raw = await file.read()
        try:
            return json.loads(file_content_raw)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON file."}