from fastapi import FastAPI, Form, Request, UploadFile, Depends, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated

from app.services.identify_source import IdentifySourceService, load_identify_source_service
from app.services.temp import TempService, get_temp_service
from app.pipeline.pipeline import Pipeline, build_pipeline
from app.models.enums import OutputFormat
from app.models.models import PipelineResponse

app = FastAPI(root_path="/hdto")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.post(
        path="/generate-rdf",
        response_model=PipelineResponse,
)
async def generate_rdf(
    pipeline: Annotated[Pipeline, Depends(build_pipeline)],
    file: UploadFile,
    output_format: Annotated[OutputFormat, Form()]
) -> PipelineResponse:
    return await pipeline.execute(file, output_format)