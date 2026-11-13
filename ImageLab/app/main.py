import json

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

import app.tools  # noqa: F401  (registers all tools)
from app.registry import TOOLS, resolve_params
from app.utils import decode_image, encode_png

app = FastAPI(title="ImgLab")

@app.get("/api/tools")
def ListTools():
    return [t.schema() for t in TOOLS.values()]

@app.post("/api/process/{tool_id}")
def process(tool_id: str, file: UploadFile = File(...), params: str = Form("{}")):
    tool = TOOLS.get(tool_id)
    if tool is None:
        raise HTTPException(404, f"Unknown tool: {tool_id}")
    try:
        raw = json.loads(params)
        kwargs = resolve_params(tool, raw)
        img = decode_image(file.file.read())
        result = tool.func(img, **kwargs)
        return Response(content=encode_png(result), media_type="image/png")
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(400, str(e))


app.mount("/", StaticFiles(directory="static", html=True), name="static")