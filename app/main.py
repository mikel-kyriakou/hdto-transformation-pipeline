import json

from fastapi import FastAPI, UploadFile, Depends, Response
from typing import Annotated

from app.services.identify_source import IdentifySourceService, load_identify_source_service
from app.services.temp import TempService, get_temp_service
from app.pipeline.pipeline import Pipeline, build_pipeline
from app.models.enums import OutputFormat

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

@app.post("/transform/temp")
async def transform_temp(
    service: Annotated[TempService, Depends(get_temp_service)],
    file: UploadFile
):
    return await service.run(file)

@app.post(
        path="/generate-rdf",
        response_model=None,
        response_class=Response,
        responses={
            200: {
                "content": {
                    "text/turtle": {"schema": {"type": "string"}},
                    "application/rdf+xml": {"schema": {"type": "string"}},
                }
            }
        }
)
async def generate_rdf(
    pipeline: Annotated[Pipeline, Depends(build_pipeline)],
    file: UploadFile,
    output_format: OutputFormat
):
    media_type = {
        OutputFormat.TTL: "text/turtle",
        OutputFormat.XML: "application/rdf+xml"
    }
    return Response(
        content=await pipeline.execute(file, output_format),
        media_type=media_type[output_format]
    )