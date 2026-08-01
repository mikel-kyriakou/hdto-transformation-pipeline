import json

from fastapi import FastAPI, UploadFile
from fastapi import Depends
from typing import Annotated

from app.services.identify_source import IdentifySourceService, load_identify_source_service

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

@app.post("/upload-file")
async def upload_file(service: Annotated[IdentifySourceService, Depends(load_identify_source_service)], file: UploadFile):

    file_content_raw = await file.read()
    try:
        file_content = json.loads(file_content_raw)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON file."}
    
    return service.identify_source(file_content)
