from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uuid
import os
import json
import mimetypes

app = FastAPI()


@app.post("/upload/")
async def upload(file: UploadFile = File(...)):
    unique_id = str(uuid.uuid4())
    dir_name = get_dir_name(unique_id)
    metadata = get_metadata(file)
    extension = mimetype_guess_extension(metadata["content_type"])

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    with open(dir_name + unique_id + extension, "wb") as f:
        contents = await file.read()
        f.write(contents)

    with open(dir_name + unique_id + ".json", "w") as f:
        f.write(json.dumps(metadata))

    return {"uuid": unique_id}


@app.get("/metadata/{uuid}")
async def retrieve_metadata(uuid: str):
    return extract_metadata(uuid)


@app.get("/get/{uuid}")
async def retrieve_file(uuid: str):
    dir_name = get_dir_name(uuid)
    try:
        metadata = extract_metadata(uuid)
        name = metadata["filename"]
        content_type = metadata["content_type"]
        extension = mimetype_guess_extension(content_type)
        target = dir_name + uuid + extension
        return FileResponse(target, filename=name, media_type=content_type)
    except:
        raise HTTPException(status_code=404, detail="Item not found")


def get_dir_name(unique_id: str):
    return "files/" + unique_id[:2] + "/" + unique_id[2:4] + "/"


def get_metadata(file: UploadFile):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": file.size,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z"),
    }


def extract_metadata(unique_id: str):
    dir_name = get_dir_name(unique_id)
    try:
        with open(dir_name + unique_id + ".json", "r") as f:
            d = json.load(f)
    except:
        raise HTTPException(status_code=404, detail="Item not found")
    return d


def mimetype_guess_extension(mimetype):
    extension = mimetypes.guess_extension(mimetype)
    return extension.lstrip(".") if extension else None
